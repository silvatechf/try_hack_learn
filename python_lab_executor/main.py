import hmac
import os
from threading import BoundedSemaphore
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from sandbox_runner import run_in_sandbox

app = FastAPI(title="SentinelForge Python Lab Internal Executor")

MAX_STUDENT_CODE_LENGTH = 10_000
MAX_TEST_CASES = 50
MAX_CONCURRENT_EXECUTIONS = int(os.getenv("PYTHON_LAB_MAX_CONCURRENT_EXECUTIONS", "2"))
if not 1 <= MAX_CONCURRENT_EXECUTIONS <= 16:
    raise RuntimeError("PYTHON_LAB_MAX_CONCURRENT_EXECUTIONS must be between 1 and 16")

EXECUTION_SLOTS = BoundedSemaphore(MAX_CONCURRENT_EXECUTIONS)
EXECUTOR_TOKEN = os.getenv("PYTHON_LAB_EXECUTOR_TOKEN")
if EXECUTOR_TOKEN is not None and len(EXECUTOR_TOKEN) < 32:
    raise RuntimeError("PYTHON_LAB_EXECUTOR_TOKEN must contain at least 32 characters")


def require_service_token(authorization: str | None = Header(default=None)):
    if not EXECUTOR_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Executor service authentication is not configured",
        )

    expected = f"Bearer {EXECUTOR_TOKEN}"
    if authorization is None or not hmac.compare_digest(authorization, expected):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ExecutionTest(BaseModel):
    input: Any
    expected: Any


class InternalExecutionRequest(BaseModel):
    exercise_id: str = Field(min_length=1, max_length=32)
    student_code: str = Field(max_length=MAX_STUDENT_CODE_LENGTH)
    tests: list[ExecutionTest] = Field(min_length=1, max_length=MAX_TEST_CASES)


@app.post("/internal/python-lab/execute", dependencies=[Depends(require_service_token)])
def internal_execute(payload: InternalExecutionRequest):
    if not EXECUTION_SLOTS.acquire(blocking=False):
        raise HTTPException(
            status_code=429,
            detail="Python Lab executor is at capacity",
            headers={"Retry-After": "2"},
        )

    try:
        tests = [test.model_dump() for test in payload.tests]
        return run_in_sandbox(payload.student_code, tests)
    finally:
        EXECUTION_SLOTS.release()

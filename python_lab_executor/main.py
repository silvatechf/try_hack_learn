from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from sandbox_runner import run_in_sandbox

app = FastAPI(title="SentinelForge Python Lab Internal Executor")

MAX_STUDENT_CODE_LENGTH = 10_000
MAX_TEST_CASES = 50


class ExecutionTest(BaseModel):
    input: Any
    expected: Any


class InternalExecutionRequest(BaseModel):
    exercise_id: str = Field(min_length=1, max_length=32)
    student_code: str = Field(max_length=MAX_STUDENT_CODE_LENGTH)
    tests: list[ExecutionTest] = Field(min_length=1, max_length=MAX_TEST_CASES)


@app.post("/internal/python-lab/execute")
def internal_execute(payload: InternalExecutionRequest):
    tests = [test.model_dump() for test in payload.tests]
    return run_in_sandbox(payload.student_code, tests)

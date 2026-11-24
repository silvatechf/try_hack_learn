import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from exercises_registry import list_exercises, get_exercise
from pedagogical_evaluator import evaluate_pedagogy
from request_limits import RequestBodyLimitMiddleware

app = FastAPI(title="SentinelForge Python Lab API")
PYTHON_LAB_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "PYTHON_LAB_ALLOWED_ORIGINS",
        "http://localhost:3001,http://127.0.0.1:3001",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=PYTHON_LAB_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

EXECUTOR_URL = "http://python_lab_executor:8003"
EXECUTOR_TOKEN = os.getenv("PYTHON_LAB_EXECUTOR_TOKEN")
if EXECUTOR_TOKEN is not None and len(EXECUTOR_TOKEN) < 32:
    raise RuntimeError("PYTHON_LAB_EXECUTOR_TOKEN must contain at least 32 characters")
MAX_STUDENT_CODE_LENGTH = 10_000
MAX_EXECUTION_REQUEST_BYTES = 64 * 1024

app.add_middleware(
    RequestBodyLimitMiddleware,
    path="/api/v1/python-lab/execute",
    max_bytes=MAX_EXECUTION_REQUEST_BYTES,
)


class ExecutionPayload(BaseModel):
    exercise_id: str = Field(min_length=1, max_length=32)
    student_code: str = Field(max_length=MAX_STUDENT_CODE_LENGTH)


@app.get("/api/v1/python-lab/exercises")
def api_list_exercises():
    return list_exercises()


@app.post("/api/v1/python-lab/execute")
async def api_execute_exercise(payload: ExecutionPayload):
    exercise = get_exercise(payload.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    if not EXECUTOR_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Python Lab executor authentication is not configured",
        )

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{EXECUTOR_URL}/internal/python-lab/execute",
                headers={"Authorization": f"Bearer {EXECUTOR_TOKEN}"},
                json={
                    "exercise_id": payload.exercise_id,
                    "student_code": payload.student_code,
                    "tests": exercise["tests"],
                },
            )
            response.raise_for_status()
            execution_result = response.json()
            if (
                not isinstance(execution_result, dict)
                or not isinstance(execution_result.get("status"), str)
            ):
                raise ValueError("Executor response has an invalid shape")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                retry_after = exc.response.headers.get("Retry-After", "2")
                if not retry_after.isdigit():
                    retry_after = "2"
                raise HTTPException(
                    status_code=429,
                    detail="Python Lab is at capacity. Retry shortly.",
                    headers={"Retry-After": retry_after},
                ) from None
            raise HTTPException(
                status_code=502,
                detail="Python Lab executor returned an unsuccessful response",
            ) from None
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Python Lab executor is unavailable",
            ) from None
        except ValueError:
            raise HTTPException(
                status_code=502,
                detail="Python Lab executor returned an invalid response",
            ) from None

    pedagogical_result = evaluate_pedagogy(exercise, execution_result)

    return {
        **execution_result,
        "exercise_id": payload.exercise_id,
        "pedagogical_result": pedagogical_result,
    }

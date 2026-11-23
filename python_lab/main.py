from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from exercises_registry import list_exercises, get_exercise
from pedagogical_evaluator import evaluate_pedagogy

app = FastAPI(title="SentinelForge Python Lab API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EXECUTOR_URL = "http://python_lab_executor:8003"
MAX_STUDENT_CODE_LENGTH = 10_000


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

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{EXECUTOR_URL}/internal/python-lab/execute",
                json={
                    "exercise_id": payload.exercise_id,
                    "student_code": payload.student_code,
                    "tests": exercise["tests"],
                },
            )
            response.raise_for_status()
            execution_result = response.json()
        except httpx.HTTPStatusError:
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

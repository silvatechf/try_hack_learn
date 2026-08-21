from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from exercises_registry import list_exercises, get_exercise

app = FastAPI(title="SentinelForge Python Lab API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EXECUTOR_URL = "http://python_lab_executor:8003"

class ExecutionPayload(BaseModel):
    exercise_id: str
    student_code: str

@app.get("/api/v1/python-lab/exercises")
def api_list_exercises():
    return list_exercises()

@app.post("/api/v1/python-lab/execute")
async def api_execute_exercise(payload: ExecutionPayload):
    exercise = get_exercise(payload.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{EXECUTOR_URL}/internal/python-lab/execute",
                json={
                    "exercise_id": payload.exercise_id,
                    "student_code": payload.student_code,
                    "tests": exercise["tests"]
                },
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Executor communication failed: {exc}")

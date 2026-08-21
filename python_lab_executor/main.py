from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sandbox_runner import run_in_sandbox

app = FastAPI(title="SentinelForge Python Lab Internal Executor")

class InternalExecutionRequest(BaseModel):
    exercise_id: str
    student_code: str
    tests: list

@app.post("/internal/python-lab/execute")
def internal_execute(payload: InternalExecutionRequest):
    result = run_in_sandbox(payload.student_code, payload.tests)
    return result

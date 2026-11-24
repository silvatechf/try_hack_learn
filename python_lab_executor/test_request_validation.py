import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import main
from main import InternalExecutionRequest


def valid_payload(**overrides):
    payload = {
        "exercise_id": "PY-001",
        "student_code": "def solve(data):\n    return sum(data)",
        "tests": [{"input": [1, 2], "expected": 3}],
    }
    payload.update(overrides)
    return payload


def test_accepts_valid_execution_payload():
    request = InternalExecutionRequest(**valid_payload())

    assert request.exercise_id == "PY-001"
    assert len(request.tests) == 1
    assert request.tests[0].expected == 3


@pytest.mark.parametrize(
    "overrides",
    [
        {"exercise_id": ""},
        {"exercise_id": "X" * 33},
        {"student_code": "x" * 10_001},
        {"tests": []},
        {"tests": [{"input": [], "expected": 0}] * 51},
        {"tests": [{"input": []}]},
    ],
)
def test_rejects_invalid_execution_payloads(overrides):
    with pytest.raises(ValidationError):
        InternalExecutionRequest(**valid_payload(**overrides))



def test_returns_429_when_execution_capacity_is_full(monkeypatch):
    from threading import BoundedSemaphore

    slots = BoundedSemaphore(1)
    monkeypatch.setattr(main, "EXECUTION_SLOTS", slots)
    assert slots.acquire(blocking=False)

    with pytest.raises(HTTPException) as exc_info:
        main.internal_execute(InternalExecutionRequest(**valid_payload()))

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "2"
    slots.release()


def test_releases_execution_slot_when_runner_raises(monkeypatch):
    from threading import BoundedSemaphore

    slots = BoundedSemaphore(1)
    monkeypatch.setattr(main, "EXECUTION_SLOTS", slots)

    def failing_runner(*args, **kwargs):
        raise RuntimeError("simulated runner failure")

    monkeypatch.setattr(main, "run_in_sandbox", failing_runner)

    with pytest.raises(RuntimeError, match="simulated runner failure"):
        main.internal_execute(InternalExecutionRequest(**valid_payload()))

    assert slots.acquire(blocking=False)
    slots.release()

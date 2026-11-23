import pytest
from pydantic import ValidationError

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

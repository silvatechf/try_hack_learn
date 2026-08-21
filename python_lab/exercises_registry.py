EXERCISES = {
    "PY-001": {
        "exercise_id": "PY-001",
        "title": "Trace the Signal",
        "difficulty": "beginner",
        "description": "Implement a function solve(data: list) -> int that returns the sum of all positive integers in the list.",
        "starter_code": "def solve(data):\n    # Write your code here\n    pass\n",
        "tests": [
            {"input": [1, -2, 3, 4], "expected": 8},
            {"input": [-5, -1, 0], "expected": 0},
            {"input": [10, 20, 30], "expected": 60}
        ],
        "learning_objectives": ["Basic iteration", "Conditional aggregation"]
    }
}

def get_exercise(exercise_id: str):
    return EXERCISES.get(exercise_id)

def list_exercises():
    return list(EXERCISES.values())

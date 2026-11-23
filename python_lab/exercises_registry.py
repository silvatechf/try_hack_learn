from typing import List, Dict, Any

EXERCISES = {
    "PY-001": {
        "exercise_id": "PY-001",
        "title_id": "exercises.py001.meta.title",
        "title": "Trace the Signal",
        "difficulty": "beginner",
        "description_id": "exercises.py001.meta.description",
        "description": "Implement a function solve(data: list) -> int that returns the sum of all positive integers in the list.",
        "learning_objectives": [
            "Basic iteration",
            "Conditional aggregation"
        ],
        "threat_context": {
            "title_id": "exercises.py001.threat.title",
            "scenario_id": "exercises.py001.threat.scenario",
            "objective_id": "exercises.py001.threat.objective"
        },
        "starter_code": "def solve(data):\n    # Write your code here\n    pass\n",
        "pedagogy": {
            "guided": {
                "steps": [
                    {
                        "id": "step_1",
                        "type": "multiple_choice",
                        "question_id": "exercises.py001.guided.step1.question",
                        "question": "What is the primary goal of this function?",
                        "option_ids": [
                            "exercises.py001.guided.step1.opt0",
                            "exercises.py001.guided.step1.opt1",
                            "exercises.py001.guided.step1.opt2"
                        ],
                        "options": [
                            "Return the length of the list",
                            "Sum all numbers in the list",
                            "Sum only the numbers strictly greater than zero"
                        ],
                        "correct_index": 2
                    },
                    {
                        "id": "step_2",
                        "type": "multiple_choice",
                        "question_id": "exercises.py001.guided.step2.question",
                        "question": "Which control structure is best suited to check every item in a list?",
                        "option_ids": [
                            "exercises.py001.guided.step2.opt0",
                            "exercises.py001.guided.step2.opt1",
                            "exercises.py001.guided.step2.opt2"
                        ],
                        "options": [
                            "if/else statement",
                            "for loop",
                            "while True loop"
                        ],
                        "correct_index": 1
                    },
                    {
                        "id": "step_3",
                        "type": "multiple_choice",
                        "question_id": "exercises.py001.guided.step3.question",
                        "question": "How do we properly check if a number 'x' is positive?",
                        "option_ids": [
                            "exercises.py001.guided.step3.opt0",
                            "exercises.py001.guided.step3.opt1",
                            "exercises.py001.guided.step3.opt2"
                        ],
                        "options": [
                            "x >= 0",
                            "x > 0",
                            "x != 0"
                        ],
                        "correct_index": 1
                    }
                ]
            },
            "assisted": {
                "starter_code": "def solve(data):\n    total = 0\n    # [ ITERATION_BLOCK ]\n\n    return total",
                "steps": [
                    {
                        "question_id": "exercises.py001.assisted.step1.question",
                        "option_ids": [
                            "exercises.py001.assisted.step1.opt0",
                            "exercises.py001.assisted.step1.opt1",
                            "exercises.py001.assisted.step1.opt2"
                        ],
                        "correct_index": 0,
                        "hint_id": "exercises.py001.assisted.step1.hint",
                        "code_snapshot": "def solve(data):\n    total = 0\n    for x in data:\n        # [ CONDITION_BLOCK ]\n\n    return total"
                    },
                    {
                        "question_id": "exercises.py001.assisted.step2.question",
                        "option_ids": [
                            "exercises.py001.assisted.step2.opt0",
                            "exercises.py001.assisted.step2.opt1",
                            "exercises.py001.assisted.step2.opt2"
                        ],
                        "correct_index": 0,
                        "hint_id": "exercises.py001.assisted.step2.hint",
                        "code_snapshot": "def solve(data):\n    total = 0\n    for x in data:\n        if x > 0:\n            # [ ACTION_BLOCK ]\n\n    return total"
                    },
                    {
                        "question_id": "exercises.py001.assisted.step3.question",
                        "option_ids": [
                            "exercises.py001.assisted.step3.opt0",
                            "exercises.py001.assisted.step3.opt1",
                            "exercises.py001.assisted.step3.opt2"
                        ],
                        "correct_index": 0,
                        "hint_id": "exercises.py001.assisted.step3.hint",
                        "code_snapshot": "def solve(data):\n    total = 0\n    for x in data:\n        if x > 0:\n            total += x\n\n    return total"
                    }
                ]
            },
            "free_code": {
                "starter_code": "def solve(data):\n    pass"
            }
        },
        "tests": [
            {"input": [1, -2, 3, 4], "expected": 8},
            {"input": [-1, -2, -3], "expected": 0},
            {"input": [], "expected": 0},
            {"input": [10, 20, -10], "expected": 30}
        ]
    }
}

def list_exercises():
    return list(EXERCISES.values())

def get_exercise(exercise_id: str):
    return EXERCISES.get(exercise_id)
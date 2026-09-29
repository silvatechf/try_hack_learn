from typing import Any


def evaluate_pedagogy(
    exercise: dict[str, Any],
    execution: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a technical execution result into a deterministic
    pedagogical result.

    This layer never executes student code and never changes
    the security execution result.
    """

    execution_status = execution.get("status")

    if execution_status == "TIMEOUT":
        return {
            "outcome": "BLOCKED",
            "feedback_key": "python_lab.feedback.timeout",
            "next_step_key": "python_lab.next_step.timeout",
            "concepts": exercise.get("learning_objectives", []),
        }

    if execution_status != "EXECUTED":
        return {
            "outcome": "ERROR",
            "feedback_key": "python_lab.feedback.execution_error",
            "next_step_key": "python_lab.next_step.execution_error",
            "concepts": exercise.get("learning_objectives", []),
        }

    evaluation = execution.get("evaluation") or {}

    evaluation_status = evaluation.get("status")

    if evaluation_status == "COMPILATION_ERROR":
        return {
            "outcome": "NEEDS_REVIEW",
            "feedback_key": "python_lab.feedback.syntax_error",
            "next_step_key": "python_lab.next_step.syntax_error",
            "concepts": exercise.get("learning_objectives", []),
        }

    if evaluation_status == "RUNTIME_ERROR":
        return {
            "outcome": "NEEDS_REVIEW",
            "feedback_key": "python_lab.feedback.runtime_error",
            "next_step_key": "python_lab.next_step.runtime_error",
            "concepts": exercise.get("learning_objectives", []),
        }

    results = evaluation.get("results") or []

    total_tests = len(results)
    passed_tests = sum(
        1 for result in results if result.get("passed") is True
    )

    passed_all = evaluation.get("passed_all") is True

    if passed_all and total_tests > 0:
        return {
            "outcome": "MASTERED",
            "feedback_key": "python_lab.feedback.mastered",
            "next_step_key": "python_lab.next_step.mastered",
            "concepts": exercise.get("learning_objectives", []),
            "score": {
                "passed": passed_tests,
                "total": total_tests,
            },
        }

    if passed_tests > 0:
        return {
            "outcome": "PRACTICE",
            "feedback_key": "python_lab.feedback.partial",
            "next_step_key": "python_lab.next_step.partial",
            "concepts": exercise.get("learning_objectives", []),
            "score": {
                "passed": passed_tests,
                "total": total_tests,
            },
        }

    return {
        "outcome": "NEEDS_REVIEW",
        "feedback_key": "python_lab.feedback.failed",
        "next_step_key": "python_lab.next_step.failed",
        "concepts": exercise.get("learning_objectives", []),
        "score": {
            "passed": passed_tests,
            "total": total_tests,
        },
    }

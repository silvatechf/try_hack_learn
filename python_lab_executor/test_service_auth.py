import pytest
from fastapi import HTTPException

import main


def test_rejects_requests_without_service_token(monkeypatch):
    monkeypatch.setattr(main, "EXECUTOR_TOKEN", "a" * 32)

    with pytest.raises(HTTPException) as exc_info:
        main.require_service_token(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


def test_rejects_incorrect_service_token(monkeypatch):
    monkeypatch.setattr(main, "EXECUTOR_TOKEN", "a" * 32)

    with pytest.raises(HTTPException) as exc_info:
        main.require_service_token("Bearer incorrect-token")

    assert exc_info.value.status_code == 401


def test_accepts_matching_service_token(monkeypatch):
    token = "a" * 32
    monkeypatch.setattr(main, "EXECUTOR_TOKEN", token)

    assert main.require_service_token(f"Bearer {token}") is None


def test_fails_closed_when_service_token_is_not_configured(monkeypatch):
    monkeypatch.setattr(main, "EXECUTOR_TOKEN", None)

    with pytest.raises(HTTPException) as exc_info:
        main.require_service_token("Bearer any-token")

    assert exc_info.value.status_code == 503


def test_service_auth_dependency_is_attached_to_execution_route():
    route = next(
        route for route in main.app.routes
        if getattr(route, "path", None) == "/internal/python-lab/execute"
    )

    dependencies = route.dependant.dependencies
    assert any(
        dependency.call is main.require_service_token
        for dependency in dependencies
    )

import os
import json
import asyncio

import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

@patch("main.httpx.AsyncClient.post")
@patch("main.run_probe_campaign")
def test_causal_loop_mission_002(mock_run_probe, mock_post):
    mock_post.return_value.status_code = 200
    mock_run_probe.side_effect = [
        {"total_probes": 50, "prevented": 0, "mitigation_percent": 0.0, "p95_latency_ms": 2.0, "availability_percent": 100.0},
        {"total_probes": 50, "prevented": 50, "mitigation_percent": 100.0, "p95_latency_ms": 22.0, "availability_percent": 100.0}
    ]
    payload = {"mission_id": "MISSION-002", "control_ids": ["data_masking", "differential_privacy"]}
    res = client.post("/api/v1/arena/deploy", json=payload)
    
    assert res.status_code == 200
    sdr = res.json()["security_decision_record"]
    assert sdr["status"] == "VALIDATED"
    assert sdr["baseline"]["prevented"] == 0

@patch("main.httpx.AsyncClient.post")
@patch("main.run_probe_campaign")
def test_mission_001_success(mock_run_probe, mock_post):
    mock_post.return_value.status_code = 200
    mock_run_probe.side_effect = [
        {"total_probes": 10, "prevented": 0, "mitigation_percent": 0.0, "p95_latency_ms": 50.0, "availability_percent": 100.0},
        {"total_probes": 10, "prevented": 10, "mitigation_percent": 100.0, "p95_latency_ms": 52.0, "availability_percent": 100.0}
    ]
    payload = {"mission_id": "MISSION-001", "control_ids": ["parameterized_queries"]}
    res = client.post("/api/v1/arena/deploy", json=payload)
    
    assert res.status_code == 200
    sdr = res.json()["security_decision_record"]
    assert sdr["status"] == "VALIDATED"
    assert sdr["latency"]["delta_ms"] == 2.0
    assert sdr["latency"]["within_budget"] is True
    assert sdr["constraints"]["passed"] is True
    assert "baseline" in sdr
    assert "observed" in sdr

@patch("main.httpx.AsyncClient.post")
@patch("main.run_probe_campaign")
def test_mission_001_failure_failure_must_teach(mock_run_probe, mock_post):
    mock_post.return_value.status_code = 200
    mock_run_probe.side_effect = [
        {"total_probes": 10, "prevented": 0, "mitigation_percent": 0.0, "p95_latency_ms": 50.0, "availability_percent": 100.0},
        {"total_probes": 10, "prevented": 0, "mitigation_percent": 0.0, "p95_latency_ms": 52.0, "availability_percent": 100.0}
    ]
    payload = {"mission_id": "MISSION-001", "control_ids": ["rate_limiting_strict"]}
    res = client.post("/api/v1/arena/deploy", json=payload)
    
    assert res.status_code == 200
    sdr = res.json()["security_decision_record"]
    assert sdr["status"] == "ARCHITECTURAL TRADE-OFF VIOLATION"
    assert len(sdr["pedagogical_feedback"]) > 0
    feedback = sdr["pedagogical_feedback"][0]
    assert "why_it_failed" in feedback
    assert "demonstrates" in feedback

@patch("main.httpx.AsyncClient.post")
@patch("main.run_probe_campaign")
def test_signed_latency_delta(mock_run_probe, mock_post):
    mock_post.return_value.status_code = 200
    mock_run_probe.side_effect = [
        {"total_probes": 10, "prevented": 0, "mitigation_percent": 0.0, "p95_latency_ms": 100.0, "availability_percent": 100.0},
        {"total_probes": 10, "prevented": 10, "mitigation_percent": 100.0, "p95_latency_ms": 90.0, "availability_percent": 100.0}
    ]
    payload = {"mission_id": "MISSION-001", "control_ids": ["parameterized_queries"]}
    res = client.post("/api/v1/arena/deploy", json=payload)
    
    assert res.status_code == 200
    sdr = res.json()["security_decision_record"]
    assert sdr["latency"]["delta_ms"] == -10.0


def test_target_api_http_failure_aborts_deployment(tmp_path):
    request = httpx.Request(
        "POST",
        "http://target_api:8000/internal/security-controls/apply",
    )
    response = httpx.Response(500, request=request)

    with patch("main.SDR_DIR", str(tmp_path)):
        with patch("main.httpx.AsyncClient.post") as mock_post:
            with patch("main.run_probe_campaign") as mock_run_probe:
                mock_post.return_value.raise_for_status.side_effect = (
                    httpx.HTTPStatusError(
                        "upstream failure",
                        request=request,
                        response=response,
                    )
                )

                result = client.post(
                    "/api/v1/arena/deploy",
                    json={
                        "mission_id": "MISSION-001",
                        "control_ids": ["parameterized_queries"],
                    },
                )

    assert result.status_code == 502
    assert result.json()["detail"] == (
        "Target API rejected the security-control update."
    )
    mock_run_probe.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_target_api_timeout_aborts_deployment(tmp_path):
    with patch("main.SDR_DIR", str(tmp_path)):
        with patch(
            "main.httpx.AsyncClient.post",
            side_effect=httpx.ReadTimeout("upstream timeout"),
        ):
            with patch("main.run_probe_campaign") as mock_run_probe:
                result = client.post(
                    "/api/v1/arena/deploy",
                    json={"mission_id": "MISSION-001", "control_ids": []},
                )

    assert result.status_code == 504
    assert result.json()["detail"] == (
        "Target API timed out while applying security controls."
    )
    mock_run_probe.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_concurrent_deployments_keep_mission_phases_serialized(tmp_path):
    events = []

    class FakeResponse:
        def raise_for_status(self):
            return None

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json, timeout):
            phase = "reset" if not json["control_ids"] else "apply"
            events.append((json["mission_id"], phase))
            await asyncio.sleep(0.005)
            return FakeResponse()

    async def fake_probe_campaign(execution_contract):
        mission_id = execution_contract["mission_id"]
        events.append((mission_id, "probe_start"))
        await asyncio.sleep(0.01)
        events.append((mission_id, "probe_end"))
        return {
            "total_probes": 1,
            "prevented": 1,
            "mitigation_percent": 100.0,
            "p95_latency_ms": 1.0,
            "availability_percent": 100.0,
        }

    def mission_for(mission_id):
        return {
            "execution_contract": {"mission_id": mission_id},
            "constraints": {
                "max_control_overhead_ms": 10.0,
                "min_availability_percent": 99.0,
            },
            "success_criteria": {"min_mitigation_percent": 90.0},
        }

    async def run_concurrent_deployments():
        return await asyncio.gather(
            main.deploy_architecture(
                {"mission_id": "MISSION-A", "control_ids": ["control-a"]}
            ),
            main.deploy_architecture(
                {"mission_id": "MISSION-B", "control_ids": ["control-b"]}
            ),
        )

    import main

    with patch("main.SDR_DIR", str(tmp_path)):
        with patch("main.get_mission", side_effect=mission_for):
            with patch("main.httpx.AsyncClient", FakeAsyncClient):
                with patch(
                    "main.run_probe_campaign",
                    side_effect=fake_probe_campaign,
                ):
                    results = asyncio.run(run_concurrent_deployments())

    expected_a = [
        ("MISSION-A", "reset"),
        ("MISSION-A", "probe_start"),
        ("MISSION-A", "probe_end"),
        ("MISSION-A", "apply"),
        ("MISSION-A", "probe_start"),
        ("MISSION-A", "probe_end"),
    ]
    expected_b = [
        ("MISSION-B", "reset"),
        ("MISSION-B", "probe_start"),
        ("MISSION-B", "probe_end"),
        ("MISSION-B", "apply"),
        ("MISSION-B", "probe_start"),
        ("MISSION-B", "probe_end"),
    ]

    assert events in (expected_a + expected_b, expected_b + expected_a)
    assert len(results) == 2
    assert all(
        result["security_decision_record"]["status"] == "VALIDATED"
        for result in results
    )

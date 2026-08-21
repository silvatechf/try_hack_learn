import os
import json
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
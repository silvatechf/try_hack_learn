import pytest
from sandbox_runner import run_in_sandbox

def test_normal_execution():
    code = "def solve(data):\n    return sum([x for x in data if x > 0])"
    tests = [{"input": [1, -2, 3, 4], "expected": 8}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["passed_all"] is True

def test_incorrect_solution():
    code = "def solve(data):\n    return 999"
    tests = [{"input": [1, -2, 3, 4], "expected": 8}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["passed_all"] is False

def test_syntax_error():
    code = "def solve(data)\n    return 1"
    tests = [{"input": [1], "expected": 1}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["status"] == "COMPILATION_ERROR"

def test_infinite_loop_timeout():
    code = "def solve(data):\n    while True: pass"
    tests = [{"input": [1, 2], "expected": 2}]
    res = run_in_sandbox(code, tests, timeout_sec=2)
    assert res["status"] == "TIMEOUT"

def test_network_isolation_enforced():
    code = """
import urllib.request
def solve(data):
    try:
        urllib.request.urlopen("http://example.com", timeout=1)
        return "NETWORK_ACCESSED"
    except Exception:
        return "NETWORK_BLOCKED"
"""
    tests = [{"input": [1], "expected": "NETWORK_BLOCKED"}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["passed_all"] is True

def test_project_filesystem_isolation():
    code = """
import os
def solve(data):
    paths_to_check = [
        "/app/docker-compose.yml",
        "/sentinelforge",
        "/orchestrator",
    ]
    found = [p for p in paths_to_check if os.path.exists(p)]
    return found
"""
    tests = [{"input": [1], "expected": []}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["passed_all"] is True

def test_docker_socket_isolation():
    code = """
import os
def solve(data):
    return os.path.exists("/var/run/docker.sock")
"""
    tests = [{"input": [1], "expected": False}]
    res = run_in_sandbox(code, tests)
    assert res["status"] == "EXECUTED"
    assert res["evaluation"]["passed_all"] is True
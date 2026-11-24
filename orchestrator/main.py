# orchestrator/main.py

import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import httpx
import subprocess
import time
from datetime import datetime

from engine.scenario_registry import get_mission, list_missions
from engine.control_registry import CONTROLS, get_control
from engine.probe_runner import run_probe_campaign


app = FastAPI(title="SentinelForge Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SDR_DIR = os.getenv("SDR_DIR", "/app/sdr_records")
os.makedirs(SDR_DIR, exist_ok=True)

TARGET_API_URL = "http://target_api:8000"

# Target API mission state is process-global. Keep the complete deployment flow
# serialized until execution state becomes request-scoped.
MISSION_EXECUTION_LOCK = asyncio.Lock()
CONTROL_APPLY_TIMEOUT_SECONDS = 10.0


async def _apply_security_controls(
    client: httpx.AsyncClient,
    mission_id: str,
    control_ids: list[str],
) -> None:
    try:
        response = await client.post(
            f"{TARGET_API_URL}/internal/security-controls/apply",
            json={
                "mission_id": mission_id,
                "control_ids": control_ids,
            },
            timeout=CONTROL_APPLY_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Target API timed out while applying security controls.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="Target API rejected the security-control update.",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Target API is unavailable while applying security controls.",
        ) from exc


def execute_sast_scan(target_dir: str):
    project_root = os.path.abspath(".")
    safe_target = os.path.abspath(target_dir)

    if not safe_target.startswith(
        os.path.join(project_root, "target_api")
    ):
        raise PermissionError("Access denied to target directory")

    start = time.perf_counter()

    try:
        result = subprocess.run(
            [
                "bandit",
                "-r",
                safe_target,
                "-f",
                "json",
                "-q",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        duration = (time.perf_counter() - start) * 1000

        findings = (
            json.loads(result.stdout)
            if result.stdout
            else {"results": []}
        )

        return {
            "findings": findings.get("results", []),
            "duration_ms": duration,
        }

    except Exception as e:
        return {
            "error": str(e),
            "duration_ms": (time.perf_counter() - start) * 1000,
        }


def summarize_sca_findings(data: dict):
    """
    Interpret the pip-audit JSON report.
    A dependency is considered vulnerable when 'vulns' contains at least one item.
    """
    dependencies = data.get("dependencies", [])
    dependencies_count = len(dependencies)
    
    vulnerable_deps = [d for d in dependencies if d.get("vulns")]
    vulnerable_dependencies_count = len(vulnerable_deps)
    
    vulnerabilities_count = sum(len(d.get("vulns", [])) for d in vulnerable_deps)

    if vulnerable_dependencies_count == 0:
        decision = "SECURE"
    else:
        decision = "VULNERABLE"

    return {
        "dependencies_count": dependencies_count,
        "vulnerable_dependencies_count": vulnerable_dependencies_count,
        "vulnerabilities_count": vulnerabilities_count,
        "decision": decision,
    }


def execute_sca_scan(req_path: str):
    project_root = os.path.abspath(".")
    safe_req = os.path.abspath(req_path)

    if not safe_req.startswith(project_root):
        raise PermissionError(
            "Access denied to requirements file"
        )

    start = time.perf_counter()

    try:
        result = subprocess.run(
            [
                "pip-audit",
                "-r",
                safe_req,
                "--format=json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        duration = (time.perf_counter() - start) * 1000

        # pip-audit returns 0 on success (no vulns) and 1 if vulnerabilities are found.
        # Both are valid execution exits for a security scan.
        if result.returncode not in [0, 1]:
            return {
                "error": f"pip-audit failed with return code {result.returncode}",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "duration_ms": duration,
            }

        # Parse output JSON safely
        try:
            report_data = json.loads(result.stdout) if result.stdout else {"dependencies": [], "fixes": []}
        except json.JSONDecodeError as jde:
            return {
                "error": f"Failed to parse pip-audit JSON output: {str(jde)}",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "duration_ms": duration,
            }

        assessment = summarize_sca_findings(report_data)
        assessment["returncode"] = result.returncode
        assessment["duration_ms"] = duration

        return {
            "report": report_data,
            "assessment": assessment,
            "duration_ms": duration,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "error": "pip-audit scan timed out after 60 seconds.",
            "duration_ms": (time.perf_counter() - start) * 1000,
            "returncode": -1,
        }
    except Exception as e:
        return {
            "error": str(e),
            "duration_ms": (
                time.perf_counter() - start
            ) * 1000,
            "returncode": -1,
        }


@app.get("/api/v1/missions/list")
def api_list_missions():
    return list_missions()


@app.get("/api/v1/controls/list")
def api_list_controls():
    return list(CONTROLS.values())


@app.post("/api/v1/arena/deploy")
async def deploy_architecture(payload: dict):
    async with MISSION_EXECUTION_LOCK:
        return await _deploy_architecture(payload)


async def _deploy_architecture(payload: dict):
    mission_id = payload.get(
        "mission_id",
        "MISSION-001",
    )

    mission = get_mission(mission_id)

    if not mission:
        raise HTTPException(
            status_code=404,
            detail=f"Mission not found: {mission_id}",
        )

    cids = payload.get("control_ids", [])

    async with httpx.AsyncClient(
        timeout=CONTROL_APPLY_TIMEOUT_SECONDS,
    ) as client:
        await _apply_security_controls(client, mission_id, [])

        baseline = await run_probe_campaign(
            mission.get("execution_contract")
        )

        await _apply_security_controls(client, mission_id, cids)

        observed = await run_probe_campaign(
            mission.get("execution_contract")
        )

    # SAST integration
    sast_results = None

    if "static_analysis_bandit" in cids:
        sast_results = execute_sast_scan("target_api")

    # SCA integration (pip-audit)
    sca_results = None

    if "dependency_analysis_safety" in cids:
        req_file = "requirements.txt"

        if os.path.exists(req_file):
            sca_results = execute_sca_scan(req_file)

    budget_ms = mission["constraints"][
        "max_control_overhead_ms"
    ]

    min_avail = mission["constraints"][
        "min_availability_percent"
    ]

    min_mit = mission["success_criteria"][
        "min_mitigation_percent"
    ]

    delta_latency_ms = (
        observed["p95_latency_ms"]
        - baseline["p95_latency_ms"]
    )

    within_budget = delta_latency_ms <= budget_ms

    within_avail = (
        observed["availability_percent"]
        >= min_avail
    )

    secure = (
        observed["mitigation_percent"]
        >= min_mit
    )

    pedagogical_feedback = []

    if secure and within_budget and within_avail:
        status = "VALIDATED"

        rationale = (
            f"Architecture validated. "
            f"Observed mitigation "
            f"({observed['mitigation_percent']}%) "
            f"met threshold ({min_mit}%)."
        )

    else:
        status = "ARCHITECTURAL TRADE-OFF VIOLATION"

        if not secure:
            rationale = (
                f"Insufficient defense-in-depth. "
                f"Observed mitigation "
                f"({observed['mitigation_percent']}%) "
                f"failed required threshold ({min_mit}%)."
            )

            for cid in cids:
                ctrl = get_control(cid)

                if ctrl and "failure_explanations" in ctrl:
                    pedagogical_feedback.append(
                        {
                            "control": ctrl["name"],
                            "layer": ctrl["layer"],
                            "why_it_failed": ctrl[
                                "failure_explanations"
                            ].get("why_it_failed", ""),
                            "demonstrates": ctrl[
                                "failure_explanations"
                            ].get("demonstrates", ""),
                        }
                    )

        else:
            rationale = (
                "Architecture violated operational constraints. "
                f"Latency budget passed: {within_budget}. "
                f"Availability constraint passed: {within_avail}."
            )

    sdr = {
        "sdr_id": (
            f"sdr-{time.time_ns()}"
        ),
        "timestamp": (
            datetime.utcnow().isoformat() + "Z"
        ),
        "mission_id": mission_id,
        "status": status,
        "controls": [
            {
                "id": control_id,
                "order": index + 1,
            }
            for index, control_id in enumerate(cids)
        ],
        "baseline": baseline,
        "observed": observed,
        "static_analysis_report": sast_results,
        "dependency_analysis_report": sca_results,
        "latency": {
            "baseline_p95_ms": (
                baseline["p95_latency_ms"]
            ),
            "observed_p95_ms": (
                observed["p95_latency_ms"]
            ),
            "delta_ms": delta_latency_ms,
            "budget_ms": budget_ms,
            "within_budget": within_budget,
        },
        "constraints": {
            "passed": (
                secure
                and within_budget
                and within_avail
            )
        },
        "architectural_rationale": rationale,
        "pedagogical_feedback": pedagogical_feedback,
    }

    sdr_path = os.path.join(
        SDR_DIR,
        sdr["sdr_id"] + ".json",
    )

    with open(
        sdr_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            sdr,
            f,
            indent=4,
        )

    return {
        "security_decision_record": sdr
    }
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re, asyncio

app = FastAPI(title="SentinelForge Target Sandbox")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Explicit Runtime Security State
RUNTIME_STATE = {
    "mission_id": "NONE",
    "active_controls": []
}

ALLOWED_CONTROLS = {
    "parameterized_queries",
    "input_sanitization",
    "rate_limiting_strict",
    "waf_rule_heavy",
    "data_masking",
    "differential_privacy",
    "semantic_guardrails",
    "output_content_filters",

    # DevSecOps controls executed by the orchestrator.
    # These controls are accepted by the runtime state,
    # but do not modify target API request/response behavior.
    "static_analysis_bandit",
    "dependency_analysis_safety",
}


class ControlApplyPayload(BaseModel):
    mission_id: str
    control_ids: list[str]


@app.post("/internal/security-controls/apply")
async def apply_security_controls(payload: ControlApplyPayload):
    invalid = [
        c for c in payload.control_ids
        if c not in ALLOWED_CONTROLS
    ]

    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Unauthorized control identifiers: {invalid}"
        )

    RUNTIME_STATE["mission_id"] = payload.mission_id
    RUNTIME_STATE["active_controls"] = payload.control_ids

    return {
        "status": "SUCCESS",
        "active_controls": RUNTIME_STATE["active_controls"]
    }


# MISSION-001 Target (SQLi)
@app.post("/api/v1/users/search")
async def search_users(payload: dict):
    query = payload.get("query", "")
    controls = RUNTIME_STATE["active_controls"]

    await asyncio.sleep(0.002)  # Base latency

    if "waf_rule_heavy" in controls:
        await asyncio.sleep(0.035)

        if re.search(r"(?i)(UNION|SELECT|OR|'|\"--)", query):
            return Response(
                status_code=403,
                content='{"error": "WAF_BLOCKED"}',
                media_type="application/json"
            )

    if "input_sanitization" in controls:
        await asyncio.sleep(0.004)

        if "'" in query or "--" in query:
            return Response(
                status_code=400,
                content='{"error": "INVALID_INPUT"}',
                media_type="application/json"
            )

    if "parameterized_queries" in controls:
        await asyncio.sleep(0.002)

        return {
            "users": [],
            "count": 0,
            "query_type": "PARAMETERIZED_SAFE"
        }

    # Vulnerability: Unsafe Concatenation
    if "' OR '" in query or "1=1" in query or "UNION" in query:
        return {
            "users": [
                {"id": i, "data": "leak"}
                for i in range(50)
            ],
            "count": 50,
            "query_type": "UNSAFE"
        }

    return {
        "users": [
            {"id": 1, "data": "alice"}
        ],
        "count": 1,
        "query_type": "UNSAFE"
    }


# MISSION-002 Target (PII Over-fetching)
@app.get("/api/v1/user/profile")
async def get_user_profile(probe_id: int = 0):
    controls = RUNTIME_STATE["active_controls"]

    if "rate_limiting_strict" in controls:
        await asyncio.sleep(0.012)

        if probe_id > 40:
            return Response(
                status_code=429,
                content='{"error": "RATE_LIMIT"}',
                media_type="application/json"
            )

    await asyncio.sleep(0.001)

    # Baseline Vulnerability: Excessive PII exposure
    data = {
        "user_id": f"usr_{probe_id}",
        "ssn": f"000-12-{1000 + probe_id}",
        "credit_card": f"4532-1111-2222-{1000 + probe_id}",
        "internal_salary": 95000 + probe_id
    }

    if "data_masking" in controls:
        await asyncio.sleep(0.001)

        data["ssn"] = "***-**-****"
        data["credit_card"] = "****-****-****-****"

    if "differential_privacy" in controls:
        await asyncio.sleep(0.018)

        data.pop("internal_salary", None)

    return data


# MISSION-003 Target (AI Prompt Injection & Tool Execution)
@app.post("/api/v1/ai/agent/execute")
async def execute_ai_agent(payload: dict):
    prompt = payload.get("prompt", "")
    controls = RUNTIME_STATE["active_controls"]

    await asyncio.sleep(0.005)

    if "semantic_guardrails" in controls:
        await asyncio.sleep(0.045)

        if any(
            kw in prompt.lower()
            for kw in [
                "ignore",
                "override",
                "bypass",
                "execute_tool"
            ]
        ):
            return Response(
                status_code=400,
                content='{"error": "GUARDRAIL_BLOCKED", "blocked": true}',
                media_type="application/json"
            )

    if "output_content_filters" in controls:
        await asyncio.sleep(0.025)

    if any(
        kw in prompt.lower()
        for kw in [
            "ignore",
            "override",
            "execute_tool"
        ]
    ):
        if "semantic_guardrails" in controls:
            return {
                "status": "success",
                "blocked": True,
                "output": (
                    "Guardrail successfully intercepted "
                    "prompt injection intent."
                )
            }

        return {
            "status": "success",
            "blocked": False,
            "output": (
                "System prompt overridden. "
                "Tool executed successfully."
            ),
            "tool_result": "records_deleted"
        }

    return {
        "status": "success",
        "blocked": False,
        "output": f"Processed prompt: {prompt}"
    }
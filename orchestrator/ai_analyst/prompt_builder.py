import json

SYSTEM_INSTRUCTION = (
    "You are an expert Cybersecurity AI Analyst for SentinelForge. "
    "Your sole responsibility is to explain what empirical security evidence means based EXCLUSIVELY on the provided Security Decision Record (SDR). "
    "GROUNDING RULES: "
    "1. Do not invent or extrapolate metrics, vulnerabilities, controls, attack results, latency, availability, or mitigation values not present in the SDR. "
    "2. Do not change, override, or dispute the deterministic status (VALIDATED or ARCHITECTURAL TRADE-OFF VIOLATION). "
    "3. Every claim must be traceable directly to the SDR JSON fields. "
    "4. Output a strictly valid JSON matching the requested schema."
)

def build_analysis_prompt(sdr: dict) -> str:
    sdr_json = json.dumps(sdr, indent=2)
    prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"SECURITY DECISION RECORD (SDR):\n{sdr_json}\n\n"
        "Provide your structured AI Security Briefing analyzing this evidence."
    )
    return prompt

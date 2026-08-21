CONTROLS = {
    "parameterized_queries": {
        "control_id": "parameterized_queries",
        "name": "Parameterized Queries",
        "layer": "Data Access / Input",
        "tradeoffs": {"latency_ms": 2, "availability_impact": 0},
        "failure_explanations": {
            "why_it_failed": "Parameterized Queries protect the SQL execution boundary against injection by separating code from data. They do not reduce the amount of data returned by a legitimate query.",
            "demonstrates": "SQL Injection and Excessive Data Exposure are different threat classes requiring controls at different architectural layers. Input protection does not guarantee output privacy."
        }
    },
    "input_sanitization": {
        "control_id": "input_sanitization",
        "name": "Input Sanitization",
        "layer": "Gateway / Input",
        "tradeoffs": {"latency_ms": 4, "availability_impact": 1},
        "failure_explanations": {
            "why_it_failed": "Removes dangerous characters from requests, but is ineffective against application logic flaws, data over-fetching, or semantic AI attacks that use natural language.",
            "demonstrates": "Gateway-level filtering cannot fix backend architectural vulnerabilities."
        }
    },
    "rate_limiting_strict": {
        "control_id": "rate_limiting_strict",
        "name": "Strict Rate Limiting",
        "layer": "Network / Gateway",
        "tradeoffs": {"latency_ms": 12, "availability_impact": 5},
        "failure_explanations": {
            "why_it_failed": "Rate limiting restricts volumetric abuse (e.g., brute force, DDoS). A single well-crafted request containing a logic flaw, SQL injection, or AI prompt bypass will succeed regardless of frequency limits.",
            "demonstrates": "Network-layer controls cannot inspect or sanitize application-layer payloads."
        }
    },
    "waf_rule_heavy": {
        "control_id": "waf_rule_heavy",
        "name": "Heavy Signature WAF",
        "layer": "Perimeter",
        "tradeoffs": {"latency_ms": 35, "availability_impact": 2},
        "failure_explanations": {
            "why_it_failed": "Blocks known attack signatures at the perimeter. It cannot protect against internal business logic flaws, legitimate-looking data over-exposure, or semantic AI attacks.",
            "demonstrates": "Perimeter defenses lack the application context needed to prevent logic-based vulnerabilities."
        }
    },
    "data_masking": {
        "control_id": "data_masking",
        "name": "Field-Level PII Masking",
        "layer": "Data / Output",
        "tradeoffs": {"latency_ms": 1, "availability_impact": 0},
        "failure_explanations": {
            "why_it_failed": "Data masking obfuscates sensitive fields in the response payload. It offers zero protection against unauthorized command execution or malicious input payloads reaching the database.",
            "demonstrates": "Output redaction does not secure the execution environment against injection vectors."
        }
    },
    "differential_privacy": {
        "control_id": "differential_privacy",
        "name": "Differential Privacy Filter",
        "layer": "Data / Output",
        "tradeoffs": {"latency_ms": 18, "availability_impact": 1},
        "failure_explanations": {
            "why_it_failed": "Adds statistical noise to datasets to protect individual identities. Completely irrelevant for preventing infrastructure exploits or SQL injections.",
            "demonstrates": "Privacy controls are not interchangeable with structural security controls."
        }
    },
    "semantic_guardrails": {
        "control_id": "semantic_guardrails",
        "name": "Semantic Input Guardrails",
        "layer": "AI / Middleware",
        "tradeoffs": {"latency_ms": 45, "availability_impact": 3},
        "failure_explanations": {
            "why_it_failed": "Evaluates prompt intent for AI systems. Adds massive latency overhead and is useless for standard web vulnerabilities like SQLi or excessive data exposure.",
            "demonstrates": "AI middleware is highly domain-specific and introduces heavy operational trade-offs if misused."
        }
    },
    "output_content_filters": {
        "control_id": "output_content_filters",
        "name": "AI Output Content Filters",
        "layer": "AI / Middleware",
        "tradeoffs": {"latency_ms": 25, "availability_impact": 2},
        "failure_explanations": {
            "why_it_failed": "Validates the output of an AI agent to prevent unauthorized data generation. Does not prevent the initial injection or protect standard databases.",
            "demonstrates": "Output validation must be paired with input validation to achieve true Defense-in-Depth."
        }
    },
    "static_analysis_bandit": {
        "control_id": "static_analysis_bandit",
        "name": "Static Analysis (Bandit)",
        "layer": "Source Code",
        "tradeoffs": {"latency_ms": 0, "availability_impact": 0},
        "failure_explanations": {
            "why_it_failed": "The code contains insecure patterns detected by static analysis.",
            "demonstrates": "Static analysis identifies vulnerabilities in the source code before execution."
        }
    },
    "dependency_analysis_safety": {
        "control_id": "dependency_analysis_safety",
        "name": "Dependency Analysis (Safety)",
        "layer": "Supply Chain / Dependencies",
        "tradeoffs": {"latency_ms": 0, "availability_impact": 0},
        "failure_explanations": {
            "why_it_failed": "The project uses dependencies with known security vulnerabilities.",
            "demonstrates": "SCA identifies supply chain risks in third-party packages."
        }
    }
}

def get_control(control_id: str):
    return CONTROLS.get(control_id)

def list_controls():
    return list(CONTROLS.values())
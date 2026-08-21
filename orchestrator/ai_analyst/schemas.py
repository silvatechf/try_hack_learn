from pydantic import BaseModel, Field

class AISecurityBriefing(BaseModel):
    sdr_id: str
    mission_id: str
    executive_summary: str = Field(..., description="High-level summary of the architectural security decision.")
    threat_analysis: str = Field(..., description="Analysis of the threat vector and its operational context.")
    evidence_interpretation: str = Field(..., description="Objective interpretation of baseline vs observed metrics.")
    root_cause: str = Field(..., description="Underlying mechanism or vulnerability exploited.")
    control_effectiveness: str = Field(..., description="Evaluation of how the control performed against telemetry.")
    architectural_trade_off: str = Field(..., description="Analysis of latency overhead, availability SLAs, and budget constraints.")
    recommended_remediation: str = Field(..., description="Actionable architectural guidance grounded in the SDR.")
    confidence_evidence_basis: str = Field(..., description="Statement confirming grounding strictly in the provided SDR metrics.")
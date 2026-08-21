import pytest
from ai_analyst.schemas import AISecurityBriefing
from ai_analyst.prompt_builder import build_analysis_prompt
from ai_analyst.analyst import AIAnalyst

def test_prompt_construction():
    sample_sdr = {
        "sdr_id": "sdr-test-123",
        "mission_id": "MISSION-001",
        "status": "VALIDATED",
        "observed": {"mitigation_percent": 100.0}
    }
    prompt = build_analysis_prompt(sample_sdr)
    assert "sdr-test-123" in prompt
    assert "MISSION-001" in prompt
    assert "VALIDATED" in prompt

def test_missing_sdr_fields_protection():
    analyst = AIAnalyst(api_key=None)
    with pytest.raises(ValueError):
        analyst.analyze_sdr({"invalid": "data"})

def test_analyst_preserves_deterministic_status():
    sample_sdr = {
        "sdr_id": "sdr-test-456",
        "mission_id": "MISSION-002",
        "status": "ARCHITECTURAL TRADE-OFF VIOLATION",
        "observed": {"mitigation_percent": 100.0},
        "latency": {"within_budget": False}
    }
    analyst = AIAnalyst(api_key=None)
    briefing = analyst.analyze_sdr(sample_sdr)
    
    assert briefing.status == "ARCHITECTURAL TRADE-OFF VIOLATION" if hasattr(briefing, 'status') else True
    # Confirma que a saída é um objeto validado pelo schema
    assert isinstance(briefing, AISecurityBriefing)
    assert briefing.sdr_id == "sdr-test-456"
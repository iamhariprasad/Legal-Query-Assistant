"""Post-generation guardrail tests."""

from app.ai.guardrails import LegalGuardrails


def test_low_confidence_triggers_refusal() -> None:
    result = LegalGuardrails().post_check(
        query="What is bail?",
        answer="Bail is discussed [1].",
        confidence=0.2,
        citations=[{"document_id": "1"}],
        min_confidence=0.62,
        min_citations=1,
    )
    assert not result.allowed
    assert result.trigger == "low_confidence"


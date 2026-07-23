"""Legal safety guardrails."""

import re

from app.ai.types import GuardrailResult, REFUSAL_MESSAGE


class LegalGuardrails:
    """Rule-based guardrails for evidence-grounded legal QA."""

    personal_patterns = [
        r"\bmy case\b",
        r"\bshould i\b",
        r"\bwhat should we do\b",
        r"\bcan i avoid\b",
        r"\bwill i win\b",
    ]
    criminal_patterns = [
        r"\bevade arrest\b",
        r"\bdestroy evidence\b",
        r"\bfake (?:evidence|alibi)\b",
        r"\bhide from police\b",
    ]
    tax_patterns = [r"\bevade tax\b", r"\bhide income\b", r"\bfake invoice\b"]
    medical_legal_patterns = [r"\bmedical negligence\b", r"\bdoctor.*liability\b", r"\bpatient consent\b"]
    prediction_patterns = [r"\bwill the court\b", r"\bguarantee\b", r"\bchances of winning\b"]

    def pre_check(self, query: str) -> GuardrailResult:
        """Check unsafe or personalized intent before generation."""
        lowered = query.lower()
        checks = [
            ("personal_legal_advice", self.personal_patterns, "Personalized legal advice requested."),
            ("criminal_advice", self.criminal_patterns, "Request may facilitate criminal wrongdoing."),
            ("tax_advice", self.tax_patterns, "Request may facilitate unlawful tax conduct."),
            (
                "medical_legal_advice",
                self.medical_legal_patterns,
                "Medical and legal advice requires qualified professional review.",
            ),
            ("future_prediction", self.prediction_patterns, "Court outcome prediction requested."),
        ]
        for trigger, patterns, reason in checks:
            if any(re.search(pattern, lowered) for pattern in patterns):
                return GuardrailResult(False, trigger=trigger, reason=reason, severity="high")
        return GuardrailResult(True)

    def post_check(
        self,
        query: str,
        answer: str,
        confidence: float,
        citations: list[dict],
        min_confidence: float,
        min_citations: int,
    ) -> GuardrailResult:
        """Check generated answer for evidence sufficiency and unsupported behavior."""
        if confidence < min_confidence:
            return GuardrailResult(False, "low_confidence", "Confidence below configured threshold.")
        if len(citations) < min_citations:
            return GuardrailResult(False, "missing_citations", "No verifiable legal citations were produced.")
        if "insufficient evidence" in answer.lower():
            return GuardrailResult(False, "insufficient_evidence", "The model reported insufficient evidence.")
        if not self.pre_check(query).allowed:
            return self.pre_check(query)
        if re.search(r"\bguarantee[sd]?\b|\bdefinitely\b|\balways\b|\bnever\b", answer.lower()):
            return GuardrailResult(False, "unsafe_response", "Answer used over-certain legal language.")
        return GuardrailResult(True)

    def refusal(self) -> str:
        """Return the standard safe refusal response."""
        return REFUSAL_MESSAGE


"""Citation verification tests."""

from app.ai.rag.citations import CitationVerifier
from app.ai.types import LegalChunk


def test_citation_verifier_rejects_missing_indices() -> None:
    verifier = CitationVerifier()
    valid, citations = verifier.verify("This has no citation.", [])
    assert not valid
    assert citations == []


def test_citation_verifier_maps_indices_to_chunks() -> None:
    chunk = LegalChunk(
        id="1:0",
        document_id="1",
        title="Case",
        source="Supreme Court",
        url="https://indiankanoon.org/doc/1/",
        text="Evidence text",
        citation="Case",
        score=0.9,
    )
    valid, citations = CitationVerifier().verify("Answer grounded in evidence [1].", [chunk])
    assert valid
    assert citations[0]["document_id"] == "1"


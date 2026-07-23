"""Prompt construction for citation-grounded legal answers."""

from app.ai.types import LegalChunk


class PromptBuilder:
    """Build strict prompts that constrain the model to retrieved evidence."""

    def build(self, query: str, chunks: list[LegalChunk]) -> str:
        """Create the final model prompt."""
        evidence = "\n\n".join(
            f"[{index}] Title: {chunk.title}\nSource: {chunk.source}\nURL: {chunk.url}\n"
            f"Excerpt: {chunk.text}"
            for index, chunk in enumerate(chunks, start=1)
        )
        return (
            "You are an Indian legal information assistant, not a lawyer. "
            "Answer ONLY from the evidence below. Do not use outside knowledge. "
            "If the evidence does not answer the question, say there is insufficient evidence. "
            "Every substantive sentence must cite one or more evidence numbers like [1]. "
            "Do not provide personalized legal strategy.\n\n"
            f"Question:\n{query}\n\nEvidence:\n{evidence}\n\n"
            "Answer with a concise explanation followed by a 'Citations' list."
        )


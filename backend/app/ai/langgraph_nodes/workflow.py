"""LangGraph workflow for citation-grounded legal question answering."""

import logging
import time
from dataclasses import asdict

from langgraph.graph import END, StateGraph

from app.ai.guardrails import LegalGuardrails
from app.ai.rag.chunker import LegalChunker
from app.ai.rag.citations import CitationVerifier
from app.ai.rag.confidence import ConfidenceScorer
from app.ai.rag.prompt import PromptBuilder
from app.ai.rag.reranker import CrossEncoderReranker
from app.ai.rag.retriever import HybridRetriever
from app.ai.types import GraphState
from app.core.config import Settings
from app.integrations.indian_kanoon import IndianKanoonClient
from app.integrations.ollama import OllamaClient

logger = logging.getLogger(__name__)


class LegalAssistantGraph:
    """Production LangGraph workflow for legal RAG."""

    def __init__(
        self,
        settings: Settings,
        indian_kanoon: IndianKanoonClient,
        retriever: HybridRetriever,
        reranker: CrossEncoderReranker,
        ollama: OllamaClient,
        chunker: LegalChunker,
        prompt_builder: PromptBuilder,
        citation_verifier: CitationVerifier,
        confidence_scorer: ConfidenceScorer,
        guardrails: LegalGuardrails,
    ) -> None:
        self.settings = settings
        self.indian_kanoon = indian_kanoon
        self.retriever = retriever
        self.reranker = reranker
        self.ollama = ollama
        self.chunker = chunker
        self.prompt_builder = prompt_builder
        self.citation_verifier = citation_verifier
        self.confidence_scorer = confidence_scorer
        self.guardrails = guardrails
        self.graph = self._build_graph()

    def _build_graph(self):
        """Compile the graph with explicit legal QA nodes."""
        graph = StateGraph(GraphState)
        graph.add_node("receive_query", self.receive_query)
        graph.add_node("search", self.search)
        graph.add_node("retrieve", self.retrieve)
        graph.add_node("rerank", self.rerank)
        graph.add_node("prompt_builder", self.build_prompt)
        graph.add_node("llm", self.generate)
        graph.add_node("confidence_evaluation", self.evaluate_confidence)
        graph.add_node("guardrail", self.apply_guardrails)
        graph.add_node("store_history", self.prepare_storage)
        graph.set_entry_point("receive_query")
        graph.add_edge("receive_query", "search")
        graph.add_edge("search", "retrieve")
        graph.add_edge("retrieve", "rerank")
        graph.add_edge("rerank", "prompt_builder")
        graph.add_edge("prompt_builder", "llm")
        graph.add_edge("llm", "confidence_evaluation")
        graph.add_edge("confidence_evaluation", "guardrail")
        graph.add_edge("guardrail", "store_history")
        graph.add_edge("store_history", END)
        return graph.compile()

    async def run(self, user_id: str, query: str) -> GraphState:
        """Execute the graph and return final state."""
        started = time.perf_counter()
        state: GraphState = {"user_id": user_id, "query": query, "metadata": {"started_at": started}}
        result: GraphState = await self.graph.ainvoke(state)
        result["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return result

    async def receive_query(self, state: GraphState) -> GraphState:
        """Validate query safety before retrieval."""
        query = state["query"].strip()
        pre = self.guardrails.pre_check(query)
        if not pre.allowed:
            state.update(
                {
                    "guardrail": pre,
                    "answer": self.guardrails.refusal(),
                    "confidence": 0.0,
                    "citations": [],
                    "refused": True,
                    "refusal_reason": pre.reason,
                }
            )
        return state

    async def search(self, state: GraphState) -> GraphState:
        """Search Indian Kanoon and fetch top documents."""
        if state.get("refused"):
            return state
        search_response = await self.indian_kanoon.search(state["query"], maxpages=1, maxcites=10)
        state["search_results"] = [result.model_dump() for result in search_response.results]
        documents = []
        for result in search_response.results[:5]:
            if result.document_id:
                try:
                    documents.append(await self.indian_kanoon.fetch_document(result.document_id))
                except Exception:
                    logger.exception("Skipping document fetch failure", extra={"request_id": "-"})
        state["documents"] = documents
        return state

    async def retrieve(self, state: GraphState) -> GraphState:
        """Chunk, index, and hybrid retrieve evidence."""
        if state.get("refused"):
            return state
        chunks = [chunk for doc in state.get("documents", []) for chunk in self.chunker.chunk(doc)]
        self.retriever.vector_store.upsert_chunks(chunks)
        state["chunks"] = chunks
        state["ranked_chunks"] = self.retriever.retrieve(state["query"], chunks, limit=12)
        return state

    async def rerank(self, state: GraphState) -> GraphState:
        """Apply cross-encoder re-ranking."""
        if state.get("refused"):
            return state
        state["ranked_chunks"] = self.reranker.rerank(
            state["query"],
            state.get("ranked_chunks", []),
            limit=self.settings.max_context_chunks,
        )
        return state

    async def build_prompt(self, state: GraphState) -> GraphState:
        """Build citation-tagged prompt."""
        if state.get("refused"):
            return state
        state["prompt"] = self.prompt_builder.build(state["query"], state.get("ranked_chunks", []))
        return state

    async def generate(self, state: GraphState) -> GraphState:
        """Generate an evidence-constrained answer."""
        if state.get("refused"):
            return state
        if not state.get("ranked_chunks"):
            state.update(
                {
                    "answer": self.guardrails.refusal(),
                    "confidence": 0.0,
                    "citations": [],
                    "refused": True,
                    "refusal_reason": "No legal evidence was retrieved.",
                }
            )
            return state
        state["answer"] = await self.ollama.generate(state["prompt"])
        return state

    async def evaluate_confidence(self, state: GraphState) -> GraphState:
        """Verify citations and score confidence."""
        if state.get("refused"):
            return state
        valid, citations = self.citation_verifier.verify(
            state.get("answer", ""), state.get("ranked_chunks", [])
        )
        if not valid and state.get("ranked_chunks"):
            state["answer"] = self._build_extractive_answer(state["query"], state["ranked_chunks"])
            valid, citations = self.citation_verifier.verify(
                state.get("answer", ""), state.get("ranked_chunks", [])
            )
        state["citations"] = citations if valid else []
        state["confidence"] = self.confidence_scorer.score(
            state.get("answer", ""), state.get("ranked_chunks", [])
        )
        return state

    async def apply_guardrails(self, state: GraphState) -> GraphState:
        """Apply final answer guardrails."""
        if state.get("refused"):
            return state
        result = self.guardrails.post_check(
            query=state["query"],
            answer=state.get("answer", ""),
            confidence=state.get("confidence", 0.0),
            citations=state.get("citations", []),
            min_confidence=self.settings.min_confidence,
            min_citations=self.settings.min_citations,
        )
        state["guardrail"] = result
        if not result.allowed:
            state.update(
                {
                    "answer": self.guardrails.refusal(),
                    "confidence": 0.0,
                    "citations": [],
                    "refused": True,
                    "refusal_reason": result.reason,
                }
            )
        else:
            state["refused"] = False
            state["refusal_reason"] = None
        return state

    async def prepare_storage(self, state: GraphState) -> GraphState:
        """Prepare serializable metadata for persistence."""
        guardrail = state.get("guardrail")
        state["metadata"] = {
            **state.get("metadata", {}),
            "search_results": state.get("search_results", []),
            "guardrail": asdict(guardrail) if guardrail else None,
            "chunks_considered": len(state.get("chunks", [])),
        }
        return state

    def _build_extractive_answer(self, query: str, chunks: list) -> str:
        """Build a citation-safe answer directly from retrieved evidence."""
        selected = chunks[: min(3, len(chunks))]
        evidence_lines = []
        for index, chunk in enumerate(selected, start=1):
            excerpt = " ".join(chunk.text.split())
            if len(excerpt) > 420:
                excerpt = excerpt[:420].rsplit(" ", 1)[0] + "."
            evidence_lines.append(f"- {excerpt} [{index}]")
        return (
            "The retrieved legal evidence indicates the following points relevant to the query. "
            "This is legal information based only on the cited sources, not personal legal advice.\n\n"
            + "\n".join(evidence_lines)
            + "\n\nCitations: "
            + ", ".join(f"[{index}] {chunk.title}" for index, chunk in enumerate(selected, start=1))
        )

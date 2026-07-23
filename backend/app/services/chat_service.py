"""Chat orchestration service."""

from collections.abc import AsyncGenerator
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guardrails import LegalGuardrails
from app.ai.langgraph_nodes.workflow import LegalAssistantGraph
from app.ai.types import REFUSAL_MESSAGE
from app.integrations.ollama import OllamaClient
from app.models.audit import GuardrailLog
from app.models.chat import ChatHistory
from app.repositories.audit_repository import GuardrailLogRepository
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatResponse


class ChatService:
    """Run legal QA and persist the result."""

    def __init__(
        self,
        session: AsyncSession,
        graph: LegalAssistantGraph,
        ollama: OllamaClient,
        guardrails: LegalGuardrails,
    ) -> None:
        self.session = session
        self.chats = ChatRepository(session)
        self.guardrail_logs = GuardrailLogRepository(session)
        self.graph = graph
        self.ollama = ollama
        self.guardrails = guardrails

    async def answer(self, user_id: str, query: str) -> ChatResponse:
        """Answer a legal query from retrieved evidence only."""
        state = await self.graph.run(user_id=user_id, query=query)
        chat = await self.chats.add(
            ChatHistory(
                user_id=user_id,
                query=query,
                answer=state.get("answer", REFUSAL_MESSAGE),
                confidence=state.get("confidence", 0.0),
                citations=state.get("citations", []),
                refused=state.get("refused", False),
                refusal_reason=state.get("refusal_reason"),
                latency_ms=state.get("latency_ms", 0),
            )
        )
        guardrail = state.get("guardrail")
        if guardrail and not guardrail.allowed:
            await self.guardrail_logs.add(
                GuardrailLog(
                    chat_id=chat.id,
                    query=query,
                    trigger=guardrail.trigger or "guardrail",
                    reason=guardrail.reason or "Guardrail blocked response.",
                    severity=guardrail.severity,
                    metadata_json=state.get("metadata", {}),
                )
            )
        return ChatResponse(
            id=chat.id,
            answer=chat.answer,
            confidence=chat.confidence,
            citations=chat.citations,
            refused=chat.refused,
            refusal_reason=chat.refusal_reason,
            latency_ms=chat.latency_ms,
            metadata=state.get("metadata", {}),
        )

    async def stream_answer(self, user_id: str, query: str) -> AsyncGenerator[str, None]:
        """Stream a completed answer as SSE while preserving guardrails."""
        response = await self.answer(user_id, query)
        yield f"event: metadata\ndata: {json.dumps({'id': response.id, 'refused': response.refused})}\n\n"
        for token in response.answer.split(" "):
            yield f"event: token\ndata: {json.dumps({'token': token + ' '})}\n\n"
        yield f"event: done\ndata: {response.model_dump_json()}\n\n"

    async def history(self, user_id: str, limit: int = 50) -> list[ChatHistory]:
        """Return a user's recent chat history."""
        return list(await self.chats.list_for_user(user_id, limit=limit))


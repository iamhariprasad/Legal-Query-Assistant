"""Chat endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guardrails import LegalGuardrails
from app.ai.langgraph_nodes.workflow import LegalAssistantGraph
from app.api.deps import current_user, graph_dep, guardrails_dep, ollama_dep
from app.db.session import get_db_session
from app.integrations.ollama import OllamaClient
from app.models.user import User
from app.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def query(
    payload: ChatRequest,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: LegalAssistantGraph = Depends(graph_dep),
    ollama: OllamaClient = Depends(ollama_dep),
    guardrails: LegalGuardrails = Depends(guardrails_dep),
) -> ChatResponse:
    """Answer a legal query with citation-grounded evidence."""
    return await ChatService(session, graph, ollama, guardrails).answer(user.id, payload.query)


@router.post("/stream")
async def stream(
    payload: ChatRequest,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: LegalAssistantGraph = Depends(graph_dep),
    ollama: OllamaClient = Depends(ollama_dep),
    guardrails: LegalGuardrails = Depends(guardrails_dep),
) -> StreamingResponse:
    """Stream a guarded response as server-sent events."""
    service = ChatService(session, graph, ollama, guardrails)
    return StreamingResponse(service.stream_answer(user.id, payload.query), media_type="text/event-stream")


@router.get("/history", response_model=list[ChatHistoryItem])
async def history(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: LegalAssistantGraph = Depends(graph_dep),
    ollama: OllamaClient = Depends(ollama_dep),
    guardrails: LegalGuardrails = Depends(guardrails_dep),
) -> list:
    """Return recent chat history."""
    return await ChatService(session, graph, ollama, guardrails).history(user.id)


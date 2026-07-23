"""FastAPI dependency injection wiring."""

from functools import lru_cache

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guardrails import LegalGuardrails
from app.ai.langgraph_nodes.workflow import LegalAssistantGraph
from app.ai.rag.bm25 import BM25Retriever
from app.ai.rag.chunker import LegalChunker
from app.ai.rag.citations import CitationVerifier
from app.ai.rag.confidence import ConfidenceScorer
from app.ai.rag.embeddings import EmbeddingModel
from app.ai.rag.prompt import PromptBuilder
from app.ai.rag.reranker import CrossEncoderReranker
from app.ai.rag.retriever import HybridRetriever
from app.ai.rag.vector_store import ChromaVectorStore
from app.core.cache import CacheClient, get_cache_client
from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.integrations.indian_kanoon import IndianKanoonClient
from app.integrations.ollama import OllamaClient
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def settings_dep() -> Settings:
    """Settings dependency."""
    return get_settings()


def cache_dep(settings: Settings = Depends(settings_dep)) -> CacheClient:
    """Cache dependency."""
    return get_cache_client(settings)


@lru_cache
def embedding_model_dep() -> EmbeddingModel:
    """Embedding model singleton."""
    return EmbeddingModel(get_settings().embedding_model)


@lru_cache
def vector_store_dep() -> ChromaVectorStore:
    """Chroma vector store singleton."""
    return ChromaVectorStore(get_settings().chroma_persist_dir, embedding_model_dep())


@lru_cache
def chunker_dep() -> LegalChunker:
    """Document chunker singleton."""
    return LegalChunker()


@lru_cache
def citation_verifier_dep() -> CitationVerifier:
    """Citation verifier singleton."""
    return CitationVerifier()


@lru_cache
def guardrails_dep() -> LegalGuardrails:
    """Guardrail singleton."""
    return LegalGuardrails()


@lru_cache
def prompt_builder_dep() -> PromptBuilder:
    """Prompt builder singleton."""
    return PromptBuilder()


@lru_cache
def reranker_dep() -> CrossEncoderReranker:
    """Cross-encoder reranker singleton."""
    return CrossEncoderReranker(get_settings().reranker_model)


def indian_kanoon_dep(
    settings: Settings = Depends(settings_dep), cache: CacheClient = Depends(cache_dep)
) -> IndianKanoonClient:
    """Indian Kanoon client dependency."""
    return IndianKanoonClient(settings, cache)


def ollama_dep(settings: Settings = Depends(settings_dep)) -> OllamaClient:
    """Ollama client dependency."""
    return OllamaClient(settings)


def graph_dep(
    settings: Settings = Depends(settings_dep),
    indian_kanoon: IndianKanoonClient = Depends(indian_kanoon_dep),
    ollama: OllamaClient = Depends(ollama_dep),
) -> LegalAssistantGraph:
    """Build graph dependency with shared heavy components."""
    vector_store = vector_store_dep()
    retriever = HybridRetriever(vector_store, BM25Retriever())
    verifier = citation_verifier_dep()
    return LegalAssistantGraph(
        settings=settings,
        indian_kanoon=indian_kanoon,
        retriever=retriever,
        reranker=reranker_dep(),
        ollama=ollama,
        chunker=chunker_dep(),
        prompt_builder=prompt_builder_dep(),
        citation_verifier=verifier,
        confidence_scorer=ConfidenceScorer(verifier),
        guardrails=guardrails_dep(),
    )


async def current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(settings_dep),
) -> User:
    """Resolve the authenticated user."""
    user_id = decode_access_token(token, settings)
    user = await UserRepository(session).get(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


async def admin_user(user: User = Depends(current_user)) -> User:
    """Require an administrator user."""
    if user.role != "admin":
        raise UnauthorizedError("Administrator privileges are required")
    return user


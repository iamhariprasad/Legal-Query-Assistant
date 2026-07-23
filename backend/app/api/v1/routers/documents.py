"""Document endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.chunker import LegalChunker
from app.ai.rag.vector_store import ChromaVectorStore
from app.api.deps import chunker_dep, current_user, indian_kanoon_dep, vector_store_dep
from app.db.session import get_db_session
from app.integrations.indian_kanoon import IndianKanoonClient
from app.models.user import User
from app.schemas.search import DocumentRead, IndexDocumentRequest, IndexDocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    _: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    indian_kanoon: IndianKanoonClient = Depends(indian_kanoon_dep),
    chunker: LegalChunker = Depends(chunker_dep),
    vector_store: ChromaVectorStore = Depends(vector_store_dep),
) -> DocumentRead:
    """Fetch a normalized Indian Kanoon document."""
    return await DocumentService(session, indian_kanoon, chunker, vector_store).fetch(document_id)


@router.post("/index", response_model=IndexDocumentResponse)
async def index_document(
    payload: IndexDocumentRequest,
    _: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    indian_kanoon: IndianKanoonClient = Depends(indian_kanoon_dep),
    chunker: LegalChunker = Depends(chunker_dep),
    vector_store: ChromaVectorStore = Depends(vector_store_dep),
) -> IndexDocumentResponse:
    """Index a document into ChromaDB."""
    return await DocumentService(session, indian_kanoon, chunker, vector_store).index(payload.document_id)


"""Search and document schemas."""

from typing import Any

from pydantic import BaseModel, Field


class LegalSearchRequest(BaseModel):
    """Indian Kanoon search request."""

    query: str = Field(min_length=3, max_length=1000)
    pagenum: int = Field(default=0, ge=0)
    maxpages: int = Field(default=1, ge=1, le=5)
    maxcites: int = Field(default=5, ge=0, le=50)


class SearchResult(BaseModel):
    """Search result document summary."""

    document_id: str
    title: str
    headline: str
    source: str
    url: str
    docsize: int | None = None
    citations: list[str] = Field(default_factory=list)


class LegalSearchResponse(BaseModel):
    """Search response."""

    query: str
    found: int
    results: list[SearchResult]
    cache_hit: bool
    latency_ms: int


class DocumentRead(BaseModel):
    """Normalized legal document response."""

    id: str | None = None
    external_id: str
    title: str
    source: str
    url: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class IndexDocumentRequest(BaseModel):
    """Request to index an Indian Kanoon document."""

    document_id: str = Field(min_length=1)
    query_hint: str | None = None

class IndexDocumentResponse(BaseModel):
    """Document indexing result."""

    document_id: str
    chunks_indexed: int


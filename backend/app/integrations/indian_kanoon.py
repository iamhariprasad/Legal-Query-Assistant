"""Indian Kanoon API integration."""

import hashlib
import logging
import re
import time
from typing import Any

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.types import LegalDocument
from app.core.cache import CacheClient
from app.core.config import Settings
from app.core.exceptions import ExternalServiceError
from app.schemas.search import LegalSearchResponse, SearchResult

logger = logging.getLogger(__name__)


class IndianKanoonClient:
    """Async client for official Indian Kanoon API endpoints."""

    def __init__(self, settings: Settings, cache: CacheClient) -> None:
        self.settings = settings
        self.cache = cache
        self.base_url = settings.indian_kanoon_base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Token {self.settings.indian_kanoon_api_token}",
        }

    @staticmethod
    def _cache_key(prefix: str, payload: str) -> str:
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"ik:{prefix}:{digest}"

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.3, min=0.3, max=3),
        reraise=True,
    )
    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a resilient API call with a POST fallback for 405 responses."""
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                url = f"{self.base_url}{path}"
                response = await client.get(url, params=params, headers=self._headers())
                if response.status_code == 405:
                    response = await client.post(url, data=params or {}, headers=self._headers())
                response.raise_for_status()
                return dict(response.json())
        except httpx.HTTPStatusError as exc:
            logger.exception("Indian Kanoon HTTP failure", extra={"request_id": "-"})
            raise ExternalServiceError(
                "Indian Kanoon API returned an error",
                status_code=exc.response.status_code,
                response_text=exc.response.text[:500],
            ) from exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            logger.exception("Indian Kanoon transport failure", extra={"request_id": "-"})
            raise

    async def search(
        self, query: str, pagenum: int = 0, maxpages: int = 1, maxcites: int = 5
    ) -> LegalSearchResponse:
        """Search Indian Kanoon and normalize results."""
        started = time.perf_counter()
        params = {
            "formInput": query,
            "pagenum": pagenum,
            "maxpages": maxpages,
            "maxcites": maxcites,
        }
        cache_key = self._cache_key("search", repr(sorted(params.items())))
        cached = await self.cache.get_json(cache_key)
        cache_hit = cached is not None
        payload = cached if isinstance(cached, dict) else await self._get("/search/", params=params)
        if not cache_hit:
            await self.cache.set_json(cache_key, payload)
        docs = payload.get("docs", [])
        results = [self._normalize_search_result(item) for item in docs if isinstance(item, dict)]
        latency_ms = int((time.perf_counter() - started) * 1000)
        return LegalSearchResponse(
            query=query,
            found=self._parse_found_count(payload.get("found"), len(results)),
            results=results,
            cache_hit=cache_hit,
            latency_ms=latency_ms,
        )

    async def fetch_document(self, document_id: str, maxcites: int = 20) -> LegalDocument:
        """Fetch and normalize a full Indian Kanoon document."""
        params = {"maxcites": maxcites, "maxcitedby": maxcites}
        cache_key = self._cache_key("doc", f"{document_id}:{maxcites}")
        cached = await self.cache.get_json(cache_key)
        payload = cached if isinstance(cached, dict) else await self._get(f"/doc/{document_id}/", params)
        if cached is None:
            await self.cache.set_json(cache_key, payload)
        html = str(payload.get("doc", ""))
        content = self._html_to_text(html)
        title = str(payload.get("title") or self._infer_title(content) or f"Indian Kanoon {document_id}")
        source = str(payload.get("docsource") or payload.get("court") or "Indian Kanoon")
        metadata = {
            "citeList": payload.get("citeList", []),
            "citedbyList": payload.get("citedbyList", []),
            "raw": {k: v for k, v in payload.items() if k != "doc"},
        }
        return LegalDocument(
            document_id=document_id,
            title=title,
            source=source,
            url=f"https://indiankanoon.org/doc/{document_id}/",
            content=content,
            metadata=metadata,
        )

    async def fetch_metadata(self, document_id: str) -> dict[str, Any]:
        """Fetch Indian Kanoon metadata for a document."""
        cache_key = self._cache_key("meta", document_id)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return cached
        payload = await self._get(f"/docmeta/{document_id}/")
        await self.cache.set_json(cache_key, payload)
        return payload

    async def fetch_fragment(self, document_id: str, query: str) -> dict[str, Any]:
        """Fetch query-specific document fragments."""
        params = {"formInput": query}
        cache_key = self._cache_key("fragment", f"{document_id}:{query}")
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return cached
        payload = await self._get(f"/docfragment/{document_id}/", params=params)
        await self.cache.set_json(cache_key, payload)
        return payload

    def _normalize_search_result(self, item: dict[str, Any]) -> SearchResult:
        """Normalize one API search result."""
        tid = str(item.get("tid") or item.get("docid") or "")
        headline = self._html_to_text(str(item.get("headline", "")))
        citations = [str(cite.get("title", cite)) for cite in item.get("citations", [])]
        return SearchResult(
            document_id=tid,
            title=self._html_to_text(str(item.get("title") or f"Indian Kanoon {tid}")),
            headline=headline,
            source=str(item.get("docsource") or "Indian Kanoon"),
            url=f"https://indiankanoon.org/doc/{tid}/",
            docsize=item.get("docsize"),
            citations=citations,
        )

    @staticmethod
    def _parse_found_count(value: Any, fallback: int) -> int:
        """Parse Indian Kanoon's found field, including strings like '1 - 10 of 993'."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            numbers = re.findall(r"\d+", value)
            if numbers:
                return int(numbers[-1])
        return fallback

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML snippets into normalized plain text."""
        soup = BeautifulSoup(html, "html.parser")
        return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()

    @staticmethod
    def _infer_title(content: str) -> str | None:
        """Infer a title from the first line of document content."""
        return content[:160].strip() if content else None

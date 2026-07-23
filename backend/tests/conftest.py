"""Pytest environment configuration."""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://legal:legal@localhost:5432/legal_assistant")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("INDIAN_KANOON_API_TOKEN", "test-token")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./.test_chroma")


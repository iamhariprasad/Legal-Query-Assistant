"""Locust load test targeting 62 requests per second."""

from __future__ import annotations

import os
from random import choice

from locust import HttpUser, between, task

QUERIES = [
    "What is anticipatory bail under Section 438 CrPC?",
    "Explain Article 21 right to privacy with citations.",
    "What is Section 138 of the Negotiable Instruments Act?",
    "What is default bail under Section 167(2) CrPC?",
]


class LegalAssistantUser(HttpUser):
    """Representative user for legal query load testing."""

    wait_time = between(0.1, 0.8)
    token: str | None = None

    def on_start(self) -> None:
        """Authenticate or reuse a token provided by the environment."""
        self.token = os.getenv("LOCUST_TOKEN")
        if self.token:
            return
        email = f"locust-{id(self)}@example.com"
        password = "locust-password-123"
        self.client.post("/api/v1/auth/register", json={"email": email, "full_name": "Locust User", "password": password})
        response = self.client.post("/api/v1/auth/login", json={"email": email, "password": password})
        if response.ok:
            self.token = response.json()["access_token"]

    @task(8)
    def legal_query(self) -> None:
        """Exercise the main RAG endpoint."""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client.post("/api/v1/chat/query", json={"query": choice(QUERIES)}, headers=headers, name="/chat/query")

    @task(2)
    def search(self) -> None:
        """Exercise Indian Kanoon search."""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client.post("/api/v1/search/legal", json={"query": choice(QUERIES)}, headers=headers, name="/search/legal")


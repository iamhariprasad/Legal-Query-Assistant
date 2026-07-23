"""CLI entrypoint for deterministic evaluation seeding."""

import asyncio

from app.db.session import AsyncSessionLocal
from app.services.evaluation_service import EvaluationService


async def main() -> None:
    """Seed deterministic evaluation rows for dashboard review."""
    async with AsyncSessionLocal() as session:
        response = await EvaluationService(session).seed_static_results()
        print(response.summary.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())

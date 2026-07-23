"""Chat and feedback persistence operations."""

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatHistory, Feedback
from app.repositories.base import Repository


class ChatRepository(Repository[ChatHistory]):
    """Repository for chat history."""

    model = ChatHistory

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_user(self, user_id: str, limit: int = 50) -> Sequence[ChatHistory]:
        """Return recent chat history for a user."""
        result = await self.session.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
        )
        return result.scalars().all()


class FeedbackRepository(Repository[Feedback]):
    """Repository for feedback."""

    model = Feedback

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)


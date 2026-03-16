"""Admin endpoints for browsing conversation messages."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import MessageOut

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageOut],
    summary="List all messages in a conversation",
)
async def list_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> list:
    # Verify conversation exists
    conv = await db.scalar(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    if not conv:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found."
        )

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()

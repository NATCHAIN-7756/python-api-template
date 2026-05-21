"""
私信/通知服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.message import Message, Notification
from app.schemas.message import MessageCreate, NotificationCreate


class MessageService:
    """私信服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sender_id: int, message_in: MessageCreate) -> Message:
        """发送私信"""
        message = Message(sender_id=sender_id, **message_in.model_dump())
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_conversation(
        self, user_id: int, other_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[Message], int]:
        """获取对话记录"""
        query = select(Message).where(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_id)) |
            ((Message.sender_id == other_id) & (Message.receiver_id == user_id))
        )
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await self.db.execute(query.order_by(Message.created_at.desc()).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def mark_read(self, user_id: int, message_ids: list[int]) -> int:
        """标记已读"""
        result = await self.db.execute(
            update(Message)
            .where(Message.id.in_(message_ids), Message.receiver_id == user_id)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.flush()
        return result.rowcount

    async def get_unread_count(self, user_id: int) -> int:
        """获取未读消息数"""
        result = await self.db.execute(
            select(func.count()).where(
                Message.receiver_id == user_id,
                Message.is_read == False,
                Message.is_deleted_by_receiver == False,
            )
        )
        return result.scalar() or 0


class NotificationService:
    """通知服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, notification_in: NotificationCreate) -> Notification:
        """创建通知"""
        notification = Notification(user_id=user_id, **notification_in.model_dump())
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_list(
        self, user_id: int, notification_type: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[Notification], int, int]:
        """获取通知列表"""
        query = select(Notification).where(Notification.user_id == user_id)
        if notification_type:
            query = query.where(Notification.type == notification_type)

        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        unread_result = await self.db.execute(
            select(func.count()).where(Notification.user_id == user_id, Notification.is_read == False)
        )
        unread = unread_result.scalar() or 0

        result = await self.db.execute(query.order_by(Notification.created_at.desc()).offset(skip).limit(limit))
        return list(result.scalars().all()), total, unread

    async def mark_read(self, user_id: int, notification_ids: list[int]) -> int:
        """标记已读"""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.id.in_(notification_ids), Notification.user_id == user_id)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.flush()
        return result.rowcount

    async def mark_all_read(self, user_id: int) -> int:
        """全部标记已读"""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.flush()
        return result.rowcount
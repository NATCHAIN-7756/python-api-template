"""
私信/通知模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Message(Base):
    """私信表"""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已读")
    is_deleted_by_sender: Mapped[bool] = mapped_column(Boolean, default=False, comment="发送者删除")
    is_deleted_by_receiver: Mapped[bool] = mapped_column(Boolean, default=False, comment="接收者删除")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="阅读时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id])

    def __repr__(self) -> str:
        return f"<Message sender={self.sender_id} receiver={self.receiver_id}>"


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, comment="类型: like/comment/follow/system")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="内容")
    related_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="关联类型")
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="关联ID")
    sender_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, comment="发送者")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已读")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="阅读时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    sender: Mapped[Optional["User"]] = relationship("User", foreign_keys=[sender_id])

    def __repr__(self) -> str:
        return f"<Notification user={self.user_id} type={self.type}>"
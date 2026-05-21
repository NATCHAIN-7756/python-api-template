"""
关注/好友模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Follow(Base):
    """关注表"""
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="关注者")
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="被关注者")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否有效")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following: Mapped["User"] = relationship("User", foreign_keys=[following_id], back_populates="followers")

    def __repr__(self) -> str:
        return f"<Follow follower={self.follower_id} following={self.following_id}>"


class Friend(Base):
    """好友表"""
    __tablename__ = "friends"
    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_friend"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="状态: pending/accepted/rejected")
    remark: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="备注名")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    friend_user: Mapped["User"] = relationship("User", foreign_keys=[friend_id])

    def __repr__(self) -> str:
        return f"<Friend user={self.user_id} friend={self.friend_id}>"
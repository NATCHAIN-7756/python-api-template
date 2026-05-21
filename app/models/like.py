"""
点赞/收藏模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Like(Base):
    """点赞表"""
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_like"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="目标类型: post/comment")
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="目标ID")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否有效")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Like user={self.user_id} target={self.target_type}:{self.target_id}>"


class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_favorite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否有效")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User")
    post: Mapped["Post"] = relationship("Post")

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} post={self.post_id}>"
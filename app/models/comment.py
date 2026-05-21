"""
评论/回复模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Comment(Base):
    """评论/回复表"""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 内容
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    content_type: Mapped[str] = mapped_column(String(20), default="text", comment="内容格式")
    
    # 关联
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False, comment="帖子ID")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="作者ID")
    
    # 回复结构
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id"), nullable=True, comment="父评论ID")
    reply_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, comment="回复用户ID")
    level: Mapped[int] = mapped_column(Integer, default=1, comment="层级")
    
    # 状态
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否隐藏")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否删除")
    
    # 统计
    likes_count: Mapped[int] = mapped_column(Integer, default=0, comment="点赞数")
    replies_count: Mapped[int] = mapped_column(Integer, default=0, comment="回复数")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], back_populates="comments")
    reply_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reply_to_id])
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id], back_populates="replies")
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent")

    def __repr__(self) -> str:
        return f"<Comment post={self.post_id} author={self.author_id}>"
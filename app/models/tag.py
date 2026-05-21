"""
标签系统
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="标签名称")
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="URL别名")
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="描述")
    
    # 显示
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="颜色")
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="图标")
    
    # 统计
    posts_count: Mapped[int] = mapped_column(Integer, default=0, comment="帖子数")
    
    # 状态
    is_hot: Mapped[bool] = mapped_column(default=False, comment="是否热门")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    posts: Mapped[list["PostTag"]] = relationship("PostTag", back_populates="tag")

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class PostTag(Base):
    """帖子标签关联表"""
    __tablename__ = "post_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联
    post: Mapped["Post"] = relationship("Post", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="posts")

    def __repr__(self) -> str:
        return f"<PostTag post={self.post_id} tag={self.tag_id}>"
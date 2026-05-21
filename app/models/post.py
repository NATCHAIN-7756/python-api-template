"""
帖子/文章模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class PostStatus(str, enum.Enum):
    """帖子状态"""
    DRAFT = "draft"       # 草稿
    PENDING = "pending"   # 待审核
    PUBLISHED = "published"  # 已发布
    REJECTED = "rejected"  # 已拒绝
    DELETED = "deleted"    # 已删除


class PostType(str, enum.Enum):
    """帖子类型"""
    ARTICLE = "article"   # 文章
    DISCUSSION = "discussion"  # 讨论
    QUESTION = "question"  # 问答
    ANNOUNCEMENT = "announcement"  # 公告


class Post(Base):
    """帖子/文章表"""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    slug: Mapped[Optional[str]] = mapped_column(String(200), unique=True, index=True, nullable=True, comment="URL别名")
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="摘要")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    content_type: Mapped[str] = mapped_column(String(20), default="markdown", comment="内容格式")
    
    # 类型与状态
    type: Mapped[PostType] = mapped_column(default=PostType.ARTICLE, comment="类型")
    status: Mapped[PostStatus] = mapped_column(default=PostStatus.DRAFT, comment="状态")
    
    # 分类
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, comment="分类ID")
    
    # 作者
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="作者ID")
    
    # 显示设置
    cover: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="封面图")
    is_top: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否置顶")
    is_hot: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否热门")
    is_recommend: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否推荐")
    
    # 权限
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    allow_comment: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许评论")
    
    # 统计
    views_count: Mapped[int] = mapped_column(Integer, default=0, comment="浏览数")
    likes_count: Mapped[int] = mapped_column(Integer, default=0, comment="点赞数")
    comments_count: Mapped[int] = mapped_column(Integer, default=0, comment="评论数")
    favorites_count: Mapped[int] = mapped_column(Integer, default=0, comment="收藏数")
    shares_count: Mapped[int] = mapped_column(Integer, default=0, comment="分享数")
    
    # 时间
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="发布时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    tags: Mapped[list["PostTag"]] = relationship("PostTag", back_populates="post")

    def __repr__(self) -> str:
        return f"<Post {self.title}>"
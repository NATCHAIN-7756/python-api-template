"""
帖子 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.models.post import PostStatus, PostType
from app.schemas.category import CategorySimple
from app.schemas.user import UserResponse


class PostBase(BaseModel):
    """帖子基础模型"""
    title: str = Field(..., min_length=2, max_length=200, description="标题")
    content: str = Field(..., min_length=1, description="内容")
    summary: Optional[str] = Field(None, max_length=500, description="摘要")


class PostCreate(PostBase):
    """帖子创建模型"""
    category_id: int = Field(..., description="分类ID")
    slug: Optional[str] = Field(None, description="URL别名")
    content_type: str = Field(default="markdown", description="内容格式")
    type: PostType = Field(default=PostType.ARTICLE, description="类型")
    cover: Optional[str] = Field(None, description="封面图")
    is_public: bool = Field(default=True, description="是否公开")
    allow_comment: bool = Field(default=True, description="允许评论")
    tags: Optional[list[str]] = Field(None, description="标签列表")


class PostUpdate(BaseModel):
    """帖子更新模型"""
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    slug: Optional[str] = None
    type: Optional[PostType] = None
    cover: Optional[str] = None
    is_public: Optional[bool] = None
    allow_comment: Optional[bool] = None
    is_top: Optional[bool] = None
    is_hot: Optional[bool] = None
    is_recommend: Optional[bool] = None
    tags: Optional[list[str]] = None


class PostResponse(PostBase):
    """帖子响应模型"""
    id: int
    slug: Optional[str]
    content_type: str
    type: PostType
    status: PostStatus
    category_id: int
    author_id: int
    cover: Optional[str]
    is_top: bool
    is_hot: bool
    is_recommend: bool
    is_public: bool
    allow_comment: bool
    views_count: int
    likes_count: int
    comments_count: int
    favorites_count: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    """帖子详情响应模型"""
    category: Optional[CategorySimple] = None
    author: Optional[UserResponse] = None
    tags: list[str] = []


class PostListResponse(BaseModel):
    """帖子列表响应"""
    total: int
    items: list[PostResponse]
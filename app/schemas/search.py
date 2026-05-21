"""
搜索 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """搜索结果项"""
    type: str = Field(..., description="类型: post/comment/user/tag")
    id: int = Field(..., description="目标ID")
    title: Optional[str] = Field(None, description="标题")
    content: str = Field(..., description="内容摘要")
    url: str = Field(..., description="跳转链接")
    score: float = Field(default=1.0, description="匹配分数")


class SearchResponse(BaseModel):
    """搜索响应"""
    keyword: str
    total: int
    items: list[SearchResult]
    took_ms: float = Field(..., description="搜索耗时(ms)")


class SearchHistoryResponse(BaseModel):
    """搜索历史响应"""
    id: int
    keyword: str
    result_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class HotSearchResponse(BaseModel):
    """热门搜索响应"""
    keyword: str
    search_count: int

    class Config:
        from_attributes = True

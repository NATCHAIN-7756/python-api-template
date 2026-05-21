"""
搜索模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SearchIndex(Base):
    """搜索索引表（用于全文搜索优化）"""
    __tablename__ = "search_indices"
    __table_args__ = (
        Index("ix_search_indices_type_target", "target_type", "target_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="目标类型: post/comment/user/tag")
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="目标ID")
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="搜索内容")
    keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="关键词")
    weight: Mapped[int] = mapped_column(Integer, default=1, comment="权重")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SearchIndex type={self.target_type} target={self.target_id}>"


class SearchHistory(Base):
    """搜索历史"""
    __tablename__ = "search_histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, comment="搜索关键词")
    result_count: Mapped[int] = mapped_column(Integer, default=0, comment="结果数量")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<SearchHistory user={self.user_id} keyword={self.keyword}>"


class HotSearch(Base):
    """热门搜索"""
    __tablename__ = "hot_searches"
    __table_args__ = (
        Index("ix_hot_searches_keyword", "keyword", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, comment="关键词")
    search_count: Mapped[int] = mapped_column(Integer, default=1, comment="搜索次数")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HotSearch keyword={self.keyword} count={self.search_count}>"

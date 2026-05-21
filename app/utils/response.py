"""
统一响应格式
SCALE OS v10.0
"""

from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应格式"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    code: int = Field(..., description="状态码")
    data: Optional[T] = Field(None, description="数据")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: str = "操作成功",
        code: int = 200,
    ) -> "ApiResponse[T]":
        """成功响应"""
        return cls(
            success=True,
            message=message,
            code=code,
            data=data,
        )

    @classmethod
    def error(
        cls,
        message: str = "操作失败",
        code: int = 400,
        data: Optional[T] = None,
    ) -> "ApiResponse[T]":
        """错误响应"""
        return cls(
            success=False,
            message=message,
            code=code,
            data=data,
        )


class PagedResponse(BaseModel, Generic[T]):
    """分页响应格式"""

    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")
    code: int = Field(default=200, description="状态码")
    data: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def create(
        cls,
        data: list[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "操作成功",
    ) -> "PagedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            message=message,
        )


class ListResponse(BaseModel, Generic[T]):
    """列表响应格式"""

    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")
    code: int = Field(default=200, description="状态码")
    data: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def create(
        cls,
        data: list[T],
        total: Optional[int] = None,
        message: str = "操作成功",
    ) -> "ListResponse[T]":
        """创建列表响应"""
        return cls(
            data=data,
            total=total if total is not None else len(data),
            message=message,
        )

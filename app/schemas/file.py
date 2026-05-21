"""
文件上传 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """文件响应模型"""
    id: int
    user_id: int
    filename: str
    stored_name: str
    path: str
    mime_type: str
    size: int
    hash: Optional[str] = None
    is_public: bool
    download_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """文件列表响应"""
    total: int
    items: list[FileResponse]


class FileUpdate(BaseModel):
    """文件更新模型"""
    is_public: Optional[bool] = Field(None, description="是否公开")


class UploadResponse(BaseModel):
    """上传响应模型"""
    id: int
    filename: str
    url: str
    size: int
    mime_type: str

    class Config:
        from_attributes = True


class FileStats(BaseModel):
    """文件统计"""
    total_files: int
    total_size: int
    by_type: dict[str, int]  # mime_type -> count

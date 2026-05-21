"""
文件上传模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    """文件表"""
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="上传者ID")
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="存储文件名(UUID)")
    path: Mapped[str] = mapped_column(String(500), nullable=False, comment="存储路径")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, comment="MIME类型")
    size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小(字节)")
    hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="文件SHA256哈希")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否公开")
    download_count: Mapped[int] = mapped_column(Integer, default=0, comment="下载次数")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<File id={self.id} filename={self.filename}>"


class FileConfig(Base):
    """文件配置表（系统级配置）"""
    __tablename__ = "file_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="配置键")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置值(JSON)")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="配置说明")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FileConfig key={self.key}>"

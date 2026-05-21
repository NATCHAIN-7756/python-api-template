"""
文件上传服务
SCALE OS v10.0
"""

import os
import hashlib
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.schemas.file import FileUpdate


# 允许的文件类型
ALLOWED_EXTENSIONS = {
    # 图片
    "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico",
    # 文档
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "md",
    # 压缩包
    "zip", "rar", "7z", "tar", "gz",
    # 音频
    "mp3", "wav", "ogg", "flac", "m4a",
    # 视频
    "mp4", "avi", "mov", "mkv", "webm",
}

# MIME 类型映射
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "txt": "text/plain",
    "md": "text/markdown",
    "zip": "application/zip",
    "mp3": "audio/mpeg",
    "mp4": "video/mp4",
}

# 文件大小限制 (字节)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


class FileService:
    """文件服务"""

    def __init__(self, db: AsyncSession, upload_dir: str = "uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    def _get_mime_type(self, filename: str) -> str:
        """获取 MIME 类型"""
        ext = self._get_extension(filename)
        return MIME_TYPES.get(ext, "application/octet-stream")

    def _generate_stored_name(self, filename: str) -> str:
        """生成存储文件名"""
        ext = self._get_extension(filename)
        return f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

    def _compute_hash(self, content: bytes) -> str:
        """计算文件哈希"""
        return hashlib.sha256(content).hexdigest()

    def _get_date_path(self) -> str:
        """获取按日期分类的存储路径"""
        now = datetime.utcnow()
        return os.path.join(str(now.year), str(now.month), str(now.day))

    async def save_file(
        self,
        user_id: int,
        filename: str,
        content: bytes,
        is_public: bool = False,
    ) -> File:
        """保存文件"""
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)")

        # 检查文件类型
        ext = self._get_extension(filename)
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}")

        # 计算哈希
        file_hash = self._compute_hash(content)

        # 检查是否已存在相同文件（去重）
        result = await self.db.execute(
            select(File).where(File.hash == file_hash)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 创建新记录指向同一文件
            new_file = File(
                user_id=user_id,
                filename=filename,
                stored_name=existing.stored_name,
                path=existing.path,
                mime_type=existing.mime_type,
                size=existing.size,
                hash=file_hash,
                is_public=is_public,
            )
            self.db.add(new_file)
            await self.db.flush()
            await self.db.refresh(new_file)
            return new_file

        # 生成存储路径
        date_path = self._get_date_path()
        stored_name = self._generate_stored_name(filename)
        relative_path = os.path.join(date_path, stored_name)
        full_path = self.upload_dir / relative_path

        # 创建目录
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(full_path, "wb") as f:
            f.write(content)

        # 创建数据库记录
        file = File(
            user_id=user_id,
            filename=filename,
            stored_name=stored_name,
            path=relative_path,
            mime_type=self._get_mime_type(filename),
            size=len(content),
            hash=file_hash,
            is_public=is_public,
        )
        self.db.add(file)
        await self.db.flush()
        await self.db.refresh(file)
        return file

    async def get_by_id(self, file_id: int) -> Optional[File]:
        """获取文件"""
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        user_id: Optional[int] = None,
        mime_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[File], int]:
        """获取文件列表"""
        query = select(File)

        if user_id:
            query = query.where(File.user_id == user_id)
        if mime_type:
            query = query.where(File.mime_type.like(f"{mime_type}%"))

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询
        query = query.offset(skip).limit(limit).order_by(File.created_at.desc())
        result = await self.db.execute(query)
        files = list(result.scalars().all())

        return files, total

    async def update(self, file_id: int, file_in: FileUpdate) -> Optional[File]:
        """更新文件信息"""
        file = await self.get_by_id(file_id)
        if not file:
            return None

        if file_in.is_public is not None:
            file.is_public = file_in.is_public

        await self.db.flush()
        await self.db.refresh(file)
        return file

    async def delete(self, file_id: int) -> bool:
        """删除文件"""
        file = await self.get_by_id(file_id)
        if not file:
            return False

        # 检查是否有其他记录指向同一文件
        result = await self.db.execute(
            select(func.count()).where(
                File.stored_name == file.stored_name,
                File.id != file_id,
            )
        )
        count = result.scalar() or 0

        # 如果没有其他记录，删除物理文件
        if count == 0:
            full_path = self.upload_dir / file.path
            if full_path.exists():
                full_path.unlink()

        # 删除数据库记录
        await self.db.delete(file)
        await self.db.flush()
        return True

    async def increment_download(self, file_id: int) -> None:
        """增加下载次数"""
        file = await self.get_by_id(file_id)
        if file:
            file.download_count += 1
            await self.db.flush()

    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """获取文件统计"""
        query = select(File)
        if user_id:
            query = query.where(File.user_id == user_id)

        result = await self.db.execute(query)
        files = list(result.scalars().all())

        # 统计
        total_files = len(files)
        total_size = sum(f.size for f in files)
        by_type: dict[str, int] = {}
        for f in files:
            mime_type = f.mime_type.split("/")[0]  # image, video, etc.
            by_type[mime_type] = by_type.get(mime_type, 0) + 1

        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": by_type,
        }

    def get_full_path(self, file: File) -> Path:
        """获取文件完整路径"""
        return self.upload_dir / file.path

"""
文件上传路由
SCALE OS v10.0
"""

import os
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse

from app.database import get_db
from app.schemas.file import (
    FileResponse, FileListResponse, FileUpdate, UploadResponse, FileStats
)
from app.services.file import FileService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()

# 上传目录
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    file: UploadFile = File(...),
    is_public: bool = Query(False, description="是否公开"),
):
    """上传文件"""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    # 读取文件内容
    content = await file.read()

    try:
        service = FileService(db, UPLOAD_DIR)
        saved_file = await service.save_file(
            user_id=current_user.id,
            filename=file.filename,
            content=content,
            is_public=is_public,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return UploadResponse(
        id=saved_file.id,
        filename=saved_file.filename,
        url=f"/files/{saved_file.id}/download",
        size=saved_file.size,
        mime_type=saved_file.mime_type,
    )


@router.post("/batch", response_model=list[UploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    files: list[UploadFile] = File(...),
    is_public: bool = Query(False, description="是否公开"),
):
    """批量上传文件"""
    if len(files) > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="最多同时上传10个文件")

    service = FileService(db, UPLOAD_DIR)
    results = []

    for file in files:
        if not file.filename:
            continue

        content = await file.read()
        try:
            saved_file = await service.save_file(
                user_id=current_user.id,
                filename=file.filename,
                content=content,
                is_public=is_public,
            )
            results.append(UploadResponse(
                id=saved_file.id,
                filename=saved_file.filename,
                url=f"/files/{saved_file.id}/download",
                size=saved_file.size,
                mime_type=saved_file.mime_type,
            ))
        except ValueError:
            continue

    return results


@router.get("/", response_model=FileListResponse)
async def get_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    mime_type: Optional[str] = Query(None, description="MIME类型过滤"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """获取文件列表"""
    service = FileService(db, UPLOAD_DIR)
    files, total = await service.get_list(
        user_id=current_user.id,
        mime_type=mime_type,
        skip=skip,
        limit=limit,
    )
    return FileListResponse(
        total=total,
        items=[FileResponse.model_validate(f) for f in files],
    )


@router.get("/stats", response_model=FileStats)
async def get_file_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取文件统计"""
    service = FileService(db, UPLOAD_DIR)
    stats = await service.get_stats(user_id=current_user.id)
    return FileStats(**stats)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取文件详情"""
    service = FileService(db, UPLOAD_DIR)
    file = await service.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 检查权限
    if file.user_id != current_user.id and not file.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问")

    return FileResponse.model_validate(file)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """下载文件"""
    service = FileService(db, UPLOAD_DIR)
    file = await service.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 检查权限
    if file.user_id != current_user.id and not file.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问")

    # 检查文件是否存在
    full_path = service.get_full_path(file)
    if not full_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 增加下载次数
    await service.increment_download(file_id)

    return FileResponse(
        path=str(full_path),
        filename=file.filename,
        media_type=file.mime_type,
    )


@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_in: FileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新文件信息"""
    service = FileService(db, UPLOAD_DIR)
    file = await service.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 检查权限
    if file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改")

    file = await service.update(file_id, file_in)
    return FileResponse.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除文件"""
    service = FileService(db, UPLOAD_DIR)
    file = await service.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 检查权限
    if file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除")

    if not await service.delete(file_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除失败")

"""
标签路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagSimple
from app.services.tag import TagService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建标签"""
    service = TagService(db)
    if await service.get_by_slug(tag_in.slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签已存在")

    tag = await service.create(tag_in)
    return TagResponse.model_validate(tag)


@router.get("/", response_model=list[TagResponse])
async def get_tags(
    skip: int = 0,
    limit: int = 50,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取标签列表"""
    service = TagService(db)
    tags = await service.get_list(skip, limit)
    return [TagResponse.model_validate(t) for t in tags]


@router.get("/hot", response_model=list[TagSimple])
async def get_hot_tags(
    limit: int = 10,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取热门标签"""
    service = TagService(db)
    tags = await service.get_hot_tags(limit)
    return [TagSimple.model_validate(t) for t in tags]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取标签详情"""
    service = TagService(db)
    tag = await service.get_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新标签"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = TagService(db)
    tag = await service.update(tag_id, tag_in)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除标签"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = TagService(db)
    if not await service.delete(tag_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
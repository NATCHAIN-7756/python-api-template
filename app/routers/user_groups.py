"""
用户组路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.user_group import (
    UserGroupCreate, UserGroupUpdate, UserGroupResponse
)
from app.services.user_group import UserGroupService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: UserGroupCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建用户组（需要管理员权限）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = UserGroupService(db)
    if await service.get_by_name(group_in.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户组已存在")

    group = await service.create(group_in)
    return UserGroupResponse.model_validate(group)


@router.get("/", response_model=list[UserGroupResponse])
async def get_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """获取用户组列表"""
    service = UserGroupService(db)
    groups = await service.get_list(skip, limit)
    return [UserGroupResponse.model_validate(g) for g in groups]


@router.get("/{group_id}", response_model=UserGroupResponse)
async def get_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取用户组详情"""
    service = UserGroupService(db)
    group = await service.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户组不存在")
    return UserGroupResponse.model_validate(group)


@router.put("/{group_id}", response_model=UserGroupResponse)
async def update_group(
    group_id: int,
    group_in: UserGroupUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新用户组"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = UserGroupService(db)
    group = await service.update(group_id, group_in)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户组不存在")
    return UserGroupResponse.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除用户组"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = UserGroupService(db)
    if not await service.delete(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户组不存在")

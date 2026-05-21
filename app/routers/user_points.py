"""
积分系统路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.user_points import UserPointsResponse, PointsLogResponse
from app.services.user_points import UserPointsService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserPointsResponse)
async def get_my_points(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取当前用户积分"""
    service = UserPointsService(db)
    points = await service.get_by_user_id(current_user.id)
    if not points:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="积分记录不存在")
    return UserPointsResponse.model_validate(points)


@router.get("/me/logs", response_model=list[PointsLogResponse])
async def get_my_points_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
):
    """获取当前用户积分日志"""
    service = UserPointsService(db)
    logs = await service.get_logs(current_user.id, skip, limit)
    return [PointsLogResponse.model_validate(log) for log in logs]


@router.get("/{user_id}", response_model=UserPointsResponse)
async def get_user_points(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取用户积分（需要登录）"""
    service = UserPointsService(db)
    points = await service.get_by_user_id(user_id)
    if not points:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="积分记录不存在")
    return UserPointsResponse.model_validate(points)

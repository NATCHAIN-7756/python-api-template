"""
用户资料路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.user_profile import UserProfileUpdate, UserProfileResponse
from app.services.user_profile import UserProfileService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取当前用户资料"""
    service = UserProfileService(db)
    profile = await service.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资料不存在")
    return UserProfileResponse.model_validate(profile)


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_in: UserProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新当前用户资料"""
    service = UserProfileService(db)
    profile = await service.update(current_user.id, profile_in)
    return UserProfileResponse.model_validate(profile)


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取用户资料"""
    service = UserProfileService(db)
    profile = await service.get_by_user_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资料不存在")
    return UserProfileResponse.model_validate(profile)

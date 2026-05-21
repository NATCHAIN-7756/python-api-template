"""
点赞/收藏路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.like import LikeCreate, LikeResponse, FavoriteCreate, FavoriteResponse, FavoriteListResponse
from app.services.like import LikeService, FavoriteService
from app.services.post import PostService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/like", response_model=LikeResponse)
async def toggle_like(
    like_in: LikeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """点赞/取消点赞"""
    service = LikeService(db)
    like, is_liked = await service.toggle(current_user.id, like_in)
    return LikeResponse.model_validate(like)


@router.post("/favorite", response_model=FavoriteResponse)
async def toggle_favorite(
    favorite_in: FavoriteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """收藏/取消收藏"""
    # 检查帖子
    post_service = PostService(db)
    post = await post_service.get_by_id(favorite_in.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="帖子不存在")

    service = FavoriteService(db)
    favorite, is_favorited = await service.toggle(current_user.id, favorite_in)
    return FavoriteResponse.model_validate(favorite)


@router.get("/favorites", response_model=FavoriteListResponse)
async def get_favorites(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
):
    """获取收藏列表"""
    service = FavoriteService(db)
    favorites, total = await service.get_list(current_user.id, skip, limit)
    return FavoriteListResponse(total=total, items=[FavoriteResponse.model_validate(f) for f in favorites])
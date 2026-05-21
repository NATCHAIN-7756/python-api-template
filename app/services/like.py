"""
点赞/收藏服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like, Favorite
from app.schemas.like import LikeCreate, FavoriteCreate


class LikeService:
    """点赞服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, user_id: int, like_in: LikeCreate) -> tuple[Like, bool]:
        """切换点赞状态，返回 (like, is_liked)"""
        result = await self.db.execute(
            select(Like).where(
                Like.user_id == user_id,
                Like.target_type == like_in.target_type,
                Like.target_id == like_in.target_id,
            )
        )
        like = result.scalar_one_or_none()

        if like:
            like.is_active = not like.is_active
            await self.db.flush()
            return like, like.is_active
        else:
            like = Like(user_id=user_id, **like_in.model_dump())
            self.db.add(like)
            await self.db.flush()
            await self.db.refresh(like)
            return like, True

    async def is_liked(self, user_id: int, target_type: str, target_id: int) -> bool:
        """检查是否已点赞"""
        result = await self.db.execute(
            select(Like).where(
                Like.user_id == user_id,
                Like.target_type == target_type,
                Like.target_id == target_id,
                Like.is_active == True,
            )
        )
        return result.scalar_one_or_none() is not None

    async def count(self, target_type: str, target_id: int) -> int:
        """获取点赞数"""
        result = await self.db.execute(
            select(func.count()).where(
                Like.target_type == target_type,
                Like.target_id == target_id,
                Like.is_active == True,
            )
        )
        return result.scalar() or 0


class FavoriteService:
    """收藏服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, user_id: int, favorite_in: FavoriteCreate) -> tuple[Favorite, bool]:
        """切换收藏状态"""
        result = await self.db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.post_id == favorite_in.post_id,
            )
        )
        favorite = result.scalar_one_or_none()

        if favorite:
            favorite.is_active = not favorite.is_active
            await self.db.flush()
            return favorite, favorite.is_active
        else:
            favorite = Favorite(user_id=user_id, **favorite_in.model_dump())
            self.db.add(favorite)
            await self.db.flush()
            await self.db.refresh(favorite)
            return favorite, True

    async def get_list(self, user_id: int, skip: int = 0, limit: int = 50) -> tuple[list[Favorite], int]:
        """获取收藏列表"""
        query = select(Favorite).where(Favorite.user_id == user_id, Favorite.is_active == True)
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Favorite.created_at.desc()))
        return list(result.scalars().all()), total

    async def is_favorited(self, user_id: int, post_id: int) -> bool:
        """检查是否已收藏"""
        result = await self.db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.post_id == post_id,
                Favorite.is_active == True,
            )
        )
        return result.scalar_one_or_none() is not None
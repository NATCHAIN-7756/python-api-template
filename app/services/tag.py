"""
标签服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag, PostTag
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    """标签服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tag_in: TagCreate) -> Tag:
        """创建标签"""
        tag = Tag(**tag_in.model_dump())
        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """根据 ID 获取标签"""
        result = await self.db.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Tag]:
        """根据 slug 获取标签"""
        result = await self.db.execute(select(Tag).where(Tag.slug == slug))
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 50) -> list[Tag]:
        """获取标签列表"""
        result = await self.db.execute(
            select(Tag).order_by(Tag.posts_count.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_hot_tags(self, limit: int = 10) -> list[Tag]:
        """获取热门标签"""
        result = await self.db.execute(
            select(Tag).where(Tag.is_hot == True).order_by(Tag.posts_count.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, tag_id: int, tag_in: TagUpdate) -> Optional[Tag]:
        """更新标签"""
        tag = await self.get_by_id(tag_id)
        if not tag:
            return None

        update_data = tag_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def delete(self, tag_id: int) -> bool:
        """删除标签"""
        tag = await self.get_by_id(tag_id)
        if not tag:
            return False
        await self.db.delete(tag)
        await self.db.flush()
        return True

    async def add_to_post(self, post_id: int, tag_ids: list[int]) -> bool:
        """为帖子添加标签"""
        for tag_id in tag_ids:
            post_tag = PostTag(post_id=post_id, tag_id=tag_id)
            self.db.add(post_tag)

            # 更新标签帖子数
            tag = await self.get_by_id(tag_id)
            if tag:
                tag.posts_count += 1

        await self.db.flush()
        return True
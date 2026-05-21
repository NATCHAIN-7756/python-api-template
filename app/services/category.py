"""
分类服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """分类服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, category_in: CategoryCreate) -> Category:
        """创建分类"""
        category = Category(**category_in.model_dump())
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """根据 ID 获取分类"""
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """根据 slug 获取分类"""
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def get_list(self, parent_id: Optional[int] = None) -> list[Category]:
        """获取分类列表"""
        query = select(Category).where(Category.is_active == True)
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        query = query.order_by(Category.sort_order, Category.id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_tree(self) -> list[Category]:
        """获取分类树"""
        result = await self.db.execute(
            select(Category).where(Category.is_active == True).order_by(Category.sort_order)
        )
        return list(result.scalars().all())

    async def update(self, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
        """更新分类"""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        update_data = category_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        """删除分类"""
        category = await self.get_by_id(category_id)
        if not category:
            return False
        category.is_active = False
        await self.db.flush()
        return True

    async def increment_posts(self, category_id: int) -> bool:
        """增加帖子数"""
        category = await self.get_by_id(category_id)
        if not category:
            return False
        category.posts_count += 1
        await self.db.flush()
        return True
"""
帖子服务
SCALE OS v10.0
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """帖子服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, author_id: int, post_in: PostCreate) -> Post:
        """创建帖子"""
        post = Post(
            author_id=author_id,
            **post_in.model_dump(exclude={"tags"}),
            status=PostStatus.DRAFT,
        )
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """根据 ID 获取帖子"""
        result = await self.db.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Post]:
        """根据 slug 获取帖子"""
        result = await self.db.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()

    async def get_list(
        self,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        status: Optional[PostStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Post], int]:
        """获取帖子列表"""
        query = select(Post)

        if category_id:
            query = query.where(Post.category_id == category_id)
        if author_id:
            query = query.where(Post.author_id == author_id)
        if status:
            query = query.where(Post.status == status)
        else:
            query = query.where(Post.status == PostStatus.PUBLISHED)

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 列表
        query = query.order_by(Post.is_top.desc(), Post.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        posts = list(result.scalars().all())

        return posts, total

    async def update(self, post_id: int, post_in: PostUpdate) -> Optional[Post]:
        """更新帖子"""
        post = await self.get_by_id(post_id)
        if not post:
            return None

        update_data = post_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def publish(self, post_id: int) -> Optional[Post]:
        """发布帖子"""
        post = await self.get_by_id(post_id)
        if not post:
            return None

        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: int) -> bool:
        """删除帖子"""
        post = await self.get_by_id(post_id)
        if not post:
            return False
        post.status = PostStatus.DELETED
        await self.db.flush()
        return True

    async def increment_views(self, post_id: int) -> bool:
        """增加浏览数"""
        post = await self.get_by_id(post_id)
        if not post:
            return False
        post.views_count += 1
        await self.db.flush()
        return True

    async def increment_likes(self, post_id: int) -> bool:
        """增加点赞数"""
        post = await self.get_by_id(post_id)
        if not post:
            return False
        post.likes_count += 1
        await self.db.flush()
        return True
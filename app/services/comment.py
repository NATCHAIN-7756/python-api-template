"""
评论服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    """评论服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, author_id: int, comment_in: CommentCreate) -> Comment:
        """创建评论"""
        comment = Comment(author_id=author_id, **comment_in.model_dump())

        # 计算层级
        if comment_in.parent_id:
            parent = await self.get_by_id(comment_in.parent_id)
            if parent:
                comment.level = parent.level + 1

        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """根据 ID 获取评论"""
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def get_list(
        self,
        post_id: int,
        parent_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Comment], int]:
        """获取评论列表"""
        query = select(Comment).where(Comment.post_id == post_id, Comment.is_hidden == False)

        if parent_id is not None:
            query = query.where(Comment.parent_id == parent_id)
        else:
            query = query.where(Comment.parent_id == None)  # 只获取一级评论

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 列表
        query = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        comments = list(result.scalars().all())

        return comments, total

    async def update(self, comment_id: int, comment_in: CommentUpdate) -> Optional[Comment]:
        """更新评论"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        update_data = comment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)

        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment_id: int) -> bool:
        """删除评论"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False
        comment.is_hidden = True
        await self.db.flush()
        return True

    async def increment_likes(self, comment_id: int) -> bool:
        """增加点赞数"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False
        comment.likes_count += 1
        await self.db.flush()
        return True
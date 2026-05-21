"""
搜索服务
SCALE OS v10.0
"""

import time
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search import SearchIndex, SearchHistory, HotSearch
from app.models.post import Post, PostStatus
from app.models.comment import Comment
from app.models.user import User
from app.models.tag import Tag
from app.schemas.search import SearchResult


class SearchService:
    """搜索服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        keyword: str,
        types: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[SearchResult], int, float]:
        """全局搜索"""
        start_time = time.time()
        
        # 默认搜索所有类型
        if not types:
            types = ["post", "comment", "user", "tag"]

        results = []
        total = 0

        # 搜索帖子
        if "post" in types:
            post_results, post_count = await self._search_posts(keyword, skip, limit)
            results.extend(post_results)
            total += post_count

        # 搜索评论
        if "comment" in types and len(results) < limit:
            comment_results, comment_count = await self._search_comments(keyword, skip, limit)
            results.extend(comment_results)
            total += comment_count

        # 搜索用户
        if "user" in types and len(results) < limit:
            user_results, user_count = await self._search_users(keyword, skip, limit)
            results.extend(user_results)
            total += user_count

        # 搜索标签
        if "tag" in types and len(results) < limit:
            tag_results, tag_count = await self._search_tags(keyword, skip, limit)
            results.extend(tag_results)
            total += tag_count

        # 按分数排序并截取
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:limit]

        took_ms = (time.time() - start_time) * 1000
        return results, total, took_ms

    async def _search_posts(self, keyword: str, skip: int, limit: int) -> tuple[list[SearchResult], int]:
        """搜索帖子"""
        query = select(Post).where(
            Post.status == PostStatus.published,
            or_(
                Post.title.ilike(f"%{keyword}%"),
                Post.content.ilike(f"%{keyword}%"),
            )
        )

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询
        query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
        result = await self.db.execute(query)
        posts = list(result.scalars().all())

        # 转换结果
        results = []
        for post in posts:
            # 计算匹配分数
            score = 1.0
            if keyword.lower() in post.title.lower():
                score = 2.0
            
            content_summary = post.content[:200] if post.content else ""
            if len(post.content or "") > 200:
                content_summary += "..."

            results.append(SearchResult(
                type="post",
                id=post.id,
                title=post.title,
                content=content_summary,
                url=f"/posts/{post.id}",
                score=score,
            ))

        return results, total

    async def _search_comments(self, keyword: str, skip: int, limit: int) -> tuple[list[SearchResult], int]:
        """搜索评论"""
        query = select(Comment).where(
            Comment.content.ilike(f"%{keyword}%")
        )

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询
        query = query.offset(skip).limit(limit).order_by(Comment.created_at.desc())
        result = await self.db.execute(query)
        comments = list(result.scalars().all())

        # 转换结果
        results = []
        for comment in comments:
            content_summary = comment.content[:200] if comment.content else ""
            if len(comment.content or "") > 200:
                content_summary += "..."

            results.append(SearchResult(
                type="comment",
                id=comment.id,
                title=None,
                content=content_summary,
                url=f"/comments/{comment.id}",
                score=1.0,
            ))

        return results, total

    async def _search_users(self, keyword: str, skip: int, limit: int) -> tuple[list[SearchResult], int]:
        """搜索用户"""
        query = select(User).where(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.nickname.ilike(f"%{keyword}%"),
            )
        )

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        # 转换结果
        results = []
        for user in users:
            results.append(SearchResult(
                type="user",
                id=user.id,
                title=user.nickname or user.username,
                content=f"用户: {user.username}",
                url=f"/users/{user.id}",
                score=1.5 if keyword.lower() in user.username.lower() else 1.0,
            ))

        return results, total

    async def _search_tags(self, keyword: str, skip: int, limit: int) -> tuple[list[SearchResult], int]:
        """搜索标签"""
        query = select(Tag).where(
            or_(
                Tag.name.ilike(f"%{keyword}%"),
                Tag.slug.ilike(f"%{keyword}%"),
            )
        )

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询
        query = query.offset(skip).limit(limit).order_by(Tag.post_count.desc())
        result = await self.db.execute(query)
        tags = list(result.scalars().all())

        # 转换结果
        results = []
        for tag in tags:
            results.append(SearchResult(
                type="tag",
                id=tag.id,
                title=tag.name,
                content=f"标签: {tag.name} ({tag.post_count} 篇帖子)",
                url=f"/tags/{tag.id}",
                score=1.0,
            ))

        return results, total

    async def save_history(self, user_id: int, keyword: str, result_count: int) -> None:
        """保存搜索历史"""
        history = SearchHistory(
            user_id=user_id,
            keyword=keyword,
            result_count=result_count,
        )
        self.db.add(history)
        await self.db.flush()

    async def get_history(self, user_id: int, limit: int = 10) -> list[SearchHistory]:
        """获取搜索历史"""
        query = select(SearchHistory).where(
            SearchHistory.user_id == user_id
        ).order_by(SearchHistory.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def clear_history(self, user_id: int) -> None:
        """清空搜索历史"""
        query = select(SearchHistory).where(SearchHistory.user_id == user_id)
        result = await self.db.execute(query)
        histories = list(result.scalars().all())
        for history in histories:
            await self.db.delete(history)
        await self.db.flush()

    async def update_hot_search(self, keyword: str) -> None:
        """更新热门搜索"""
        result = await self.db.execute(
            select(HotSearch).where(HotSearch.keyword == keyword)
        )
        hot = result.scalar_one_or_none()

        if hot:
            hot.search_count += 1
        else:
            hot = HotSearch(keyword=keyword, search_count=1)
            self.db.add(hot)

        await self.db.flush()

    async def get_hot_searches(self, limit: int = 10) -> list[HotSearch]:
        """获取热门搜索"""
        # 最近7天的热门搜索
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        query = select(HotSearch).where(
            HotSearch.updated_at >= seven_days_ago
        ).order_by(HotSearch.search_count.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
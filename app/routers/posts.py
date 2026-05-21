"""
帖子路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.models.post import PostStatus
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostDetailResponse, PostListResponse
)
from app.services.post import PostService
from app.services.category import CategoryService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建帖子"""
    # 检查分类
    category_service = CategoryService(db)
    category = await category_service.get_by_id(post_in.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在")

    service = PostService(db)
    post = await service.create(current_user.id, post_in)
    return PostResponse.model_validate(post)


@router.get("/", response_model=PostListResponse)
async def get_posts(
    category_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    status: Optional[PostStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取帖子列表"""
    service = PostService(db)
    posts, total = await service.get_list(category_id, author_id, status, skip, limit)
    return PostListResponse(
        total=total,
        items=[PostResponse.model_validate(p) for p in posts],
    )


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取帖子详情"""
    service = PostService(db)
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    # 增加浏览数
    await service.increment_views(post_id)

    return PostDetailResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新帖子"""
    service = PostService(db)
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    # 检查权限
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    post = await service.update(post_id, post_in)
    return PostResponse.model_validate(post)


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """发布帖子"""
    service = PostService(db)
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    post = await service.publish(post_id)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除帖子"""
    service = PostService(db)
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    await service.delete(post_id)


@router.post("/{post_id}/like", response_model=PostResponse)
async def like_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """点赞帖子"""
    service = PostService(db)
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    await service.increment_likes(post_id)
    post = await service.get_by_id(post_id)
    return PostResponse.model_validate(post)
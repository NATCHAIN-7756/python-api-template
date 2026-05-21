"""
评论路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, CommentDetailResponse, CommentListResponse
)
from app.services.comment import CommentService
from app.services.post import PostService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_in: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建评论"""
    # 检查帖子
    post_service = PostService(db)
    post = await post_service.get_by_id(comment_in.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="帖子不存在")

    if not post.allow_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="帖子不允许评论")

    service = CommentService(db)
    comment = await service.create(current_user.id, comment_in)
    return CommentResponse.model_validate(comment)


@router.get("/", response_model=CommentListResponse)
async def get_comments(
    post_id: int = Query(...),
    parent_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取评论列表"""
    service = CommentService(db)
    comments, total = await service.get_list(post_id, parent_id, skip, limit)
    return CommentListResponse(
        total=total,
        items=[CommentResponse.model_validate(c) for c in comments],
    )


@router.get("/{comment_id}", response_model=CommentDetailResponse)
async def get_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取评论详情"""
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return CommentDetailResponse.model_validate(comment)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新评论"""
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    comment = await service.update(comment_id, comment_in)
    return CommentResponse.model_validate(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除评论"""
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    await service.delete(comment_id)


@router.post("/{comment_id}/like", response_model=CommentResponse)
async def like_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """点赞评论"""
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    await service.increment_likes(comment_id)
    comment = await service.get_by_id(comment_id)
    return CommentResponse.model_validate(comment)
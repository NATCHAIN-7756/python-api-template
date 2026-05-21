"""
管理后台路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.post import Post, PostStatus
from app.models.comment import Comment
from app.models.file import File
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


def require_admin(current_user: UserResponse) -> None:
    """检查管理员权限"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )


# ============ 仪表盘 ============

@router.get("/dashboard")
async def get_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取仪表盘数据"""
    require_admin(current_user)

    # 用户统计
    user_count = await db.execute(select(func.count()).select_from(User))
    total_users = user_count.scalar() or 0

    # 帖子统计
    post_count = await db.execute(select(func.count()).select_from(Post))
    total_posts = post_count.scalar() or 0

    # 评论统计
    comment_count = await db.execute(select(func.count()).select_from(Comment))
    total_comments = comment_count.scalar() or 0

    # 文件统计
    file_count = await db.execute(select(func.count()).select_from(File))
    total_files = file_count.scalar() or 0

    # 待审核帖子
    pending_posts = await db.execute(
        select(func.count()).select_from(Post).where(Post.status == PostStatus.draft)
    )
    pending_count = pending_posts.scalar() or 0

    return {
        "users": total_users,
        "posts": total_posts,
        "comments": total_comments,
        "files": total_files,
        "pending_posts": pending_count,
    }


# ============ 用户管理 ============

@router.get("/users")
async def admin_list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_superuser: Optional[bool] = Query(None),
):
    """管理员获取用户列表"""
    require_admin(current_user)

    query = select(User)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if is_superuser is not None:
        query = query.where(User.is_superuser == is_superuser)

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 查询
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = list(result.scalars().all())

    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "nickname": u.nickname,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.post("/users/{user_id}/activate")
async def admin_activate_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """激活/禁用用户"""
    require_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = not user.is_active
    await db.flush()

    return {"id": user.id, "is_active": user.is_active}


@router.post("/users/{user_id}/promote")
async def admin_promote_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """设置/取消管理员"""
    require_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能取消自己的管理员权限
    if user.id == current_user.id and user.is_superuser:
        raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")

    user.is_superuser = not user.is_superuser
    await db.flush()

    return {"id": user.id, "is_superuser": user.is_superuser}


# ============ 帖子管理 ============

@router.get("/posts")
async def admin_list_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[PostStatus] = Query(None, alias="status"),
):
    """管理员获取帖子列表"""
    require_admin(current_user)

    query = select(Post)

    if status_filter:
        query = query.where(Post.status == status_filter)

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 查询
    query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
    result = await db.execute(query)
    posts = list(result.scalars().all())

    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "title": p.title,
                "author_id": p.author_id,
                "status": p.status.value,
                "views": p.views,
                "likes": p.likes,
                "created_at": p.created_at,
            }
            for p in posts
        ],
    }


@router.post("/posts/{post_id}/approve")
async def admin_approve_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """审核通过帖子"""
    require_admin(current_user)

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    post.status = PostStatus.published
    await db.flush()

    return {"id": post.id, "status": post.status.value}


@router.post("/posts/{post_id}/reject")
async def admin_reject_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """拒绝帖子"""
    require_admin(current_user)

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    post.status = PostStatus.archived
    await db.flush()

    return {"id": post.id, "status": post.status.value}


@router.delete("/posts/{post_id}")
async def admin_delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """管理员删除帖子"""
    require_admin(current_user)

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    await db.delete(post)
    await db.flush()

    return {"message": "删除成功"}


# ============ 评论管理 ============

@router.get("/comments")
async def admin_list_comments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """管理员获取评论列表"""
    require_admin(current_user)

    query = select(Comment)

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 查询
    query = query.offset(skip).limit(limit).order_by(Comment.created_at.desc())
    result = await db.execute(query)
    comments = list(result.scalars().all())

    return {
        "total": total,
        "items": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "author_id": c.author_id,
                "content": c.content[:100] + "..." if len(c.content or "") > 100 else c.content,
                "likes": c.likes,
                "created_at": c.created_at,
            }
            for c in comments
        ],
    }


@router.delete("/comments/{comment_id}")
async def admin_delete_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """管理员删除评论"""
    require_admin(current_user)

    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    await db.delete(comment)
    await db.flush()

    return {"message": "删除成功"}


# ============ 文件管理 ============

@router.get("/files")
async def admin_list_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """管理员获取文件列表"""
    require_admin(current_user)

    query = select(File)

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 查询
    query = query.offset(skip).limit(limit).order_by(File.created_at.desc())
    result = await db.execute(query)
    files = list(result.scalars().all())

    return {
        "total": total,
        "items": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "filename": f.filename,
                "mime_type": f.mime_type,
                "size": f.size,
                "is_public": f.is_public,
                "download_count": f.download_count,
                "created_at": f.created_at,
            }
            for f in files
        ],
    }


@router.delete("/files/{file_id}")
async def admin_delete_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """管理员删除文件"""
    require_admin(current_user)

    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")

    await db.delete(file)
    await db.flush()

    return {"message": "删除成功"}
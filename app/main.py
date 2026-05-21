"""
Python API Template - FastAPI 入口
SCALE OS v10.0
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config import settings
from app.middleware.logging import LoggingMiddleware
from app.middleware.error import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    general_exception_handler,
)
from app.routers import (
    health, auth, users,
    user_groups, user_profiles, user_points,
    categories, posts, comments, tags,
    likes, follows, messages, files
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"[SCALE] {settings.APP_NAME} 启动...")
    print(f"[SCALE] 环境: {settings.APP_ENV}")
    print(f"[SCALE] 版本: {settings.SCALE_VERSION}")
    yield
    print(f"[SCALE] {settings.APP_NAME} 关闭...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Python API 模板 - SCALE OS v10.0",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 日志中间件
app.add_middleware(LoggingMiddleware)

# 异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户"])
app.include_router(user_groups.router, prefix="/groups", tags=["用户组"])
app.include_router(user_profiles.router, prefix="/profiles", tags=["用户资料"])
app.include_router(user_points.router, prefix="/points", tags=["积分"])
app.include_router(categories.router, prefix="/categories", tags=["分类"])
app.include_router(posts.router, prefix="/posts", tags=["帖子"])
app.include_router(comments.router, prefix="/comments", tags=["评论"])
app.include_router(tags.router, prefix="/tags", tags=["标签"])
app.include_router(likes.router, prefix="/interactions", tags=["点赞收藏"])
app.include_router(follows.router, prefix="/social", tags=["关注好友"])
app.include_router(messages.router, prefix="/messages", tags=["私信通知"])
app.include_router(files.router, prefix="/files", tags=["文件上传"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "scale_version": settings.SCALE_VERSION,
        "env": settings.APP_ENV,
    }
"""
Python API Template - FastAPI 入口
SCALE OS v10.0
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    health, auth, users,
    user_groups, user_profiles, user_points
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"[SCALE] {settings.APP_NAME} 启动...")
    yield
    # 关闭时
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

# 路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户"])
app.include_router(user_groups.router, prefix="/groups", tags=["用户组"])
app.include_router(user_profiles.router, prefix="/profiles", tags=["用户资料"])
app.include_router(user_points.router, prefix="/points", tags=["积分"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "scale_version": "10.0",
    }
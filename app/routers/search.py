"""
搜索路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas.search import (
    SearchResponse, SearchResult, SearchHistoryResponse, HotSearchResponse
)
from app.services.search import SearchService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def global_search(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    keyword: str = Query(..., min_length=1, max_length=200, description="搜索关键词"),
    types: Optional[str] = Query(None, description="搜索类型: post,comment,user,tag"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """全局搜索"""
    # 解析类型
    type_list = types.split(",") if types else None

    service = SearchService(db)
    results, total, took_ms = await service.search(keyword, type_list, skip, limit)

    # 保存搜索历史
    await service.save_history(current_user.id, keyword, total)

    # 更新热门搜索
    await service.update_hot_search(keyword)

    return SearchResponse(
        keyword=keyword,
        total=total,
        items=results,
        took_ms=took_ms,
    )


@router.get("/posts", response_model=list[SearchResult])
async def search_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    keyword: str = Query(..., min_length=1, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """搜索帖子"""
    service = SearchService(db)
    results, total = await service._search_posts(keyword, skip, limit)
    return results


@router.get("/users", response_model=list[SearchResult])
async def search_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    keyword: str = Query(..., min_length=1, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """搜索用户"""
    service = SearchService(db)
    results, total = await service._search_users(keyword, skip, limit)
    return results


@router.get("/tags", response_model=list[SearchResult])
async def search_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    keyword: str = Query(..., min_length=1, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """搜索标签"""
    service = SearchService(db)
    results, total = await service._search_tags(keyword, skip, limit)
    return results


@router.get("/history", response_model=list[SearchHistoryResponse])
async def get_search_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
):
    """获取搜索历史"""
    service = SearchService(db)
    histories = await service.get_history(current_user.id, limit)
    return [SearchHistoryResponse.model_validate(h) for h in histories]


@router.delete("/history", status_code=204)
async def clear_search_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """清空搜索历史"""
    service = SearchService(db)
    await service.clear_history(current_user.id)


@router.get("/hot", response_model=list[HotSearchResponse])
async def get_hot_searches(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    """获取热门搜索"""
    service = SearchService(db)
    hot_searches = await service.get_hot_searches(limit)
    return [HotSearchResponse.model_validate(h) for h in hot_searches]
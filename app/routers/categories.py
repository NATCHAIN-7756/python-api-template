"""
分类路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse
)
from app.services.category import CategoryService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建分类"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = CategoryService(db)
    if await service.get_by_slug(category_in.slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分类已存在")

    category = await service.create(category_in)
    return CategoryResponse.model_validate(category)


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    parent_id: int = None,
):
    """获取分类列表"""
    service = CategoryService(db)
    categories = await service.get_list(parent_id)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/tree", response_model=list[CategoryTreeResponse])
async def get_category_tree(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取分类树"""
    service = CategoryService(db)
    categories = await service.get_tree()

    # 构建树结构
    def build_tree(items: list, parent_id: int = None) -> list:
        children = [c for c in items if c.parent_id == parent_id]
        result = []
        for child in children:
            tree_item = CategoryTreeResponse.model_validate(child)
            tree_item.children = build_tree(items, child.id)
            result.append(tree_item)
        return result

    return build_tree(categories)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取分类详情"""
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新分类"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = CategoryService(db)
    category = await service.update(category_id, category_in)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除分类"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = CategoryService(db)
    if not await service.delete(category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
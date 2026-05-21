"""
菜单服务
SCALE OS v10.0
"""

from typing import Optional, List
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.menu import Menu, MenuItem, UserMenu
from app.core.hook import hooks


class MenuService:
    """菜单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        name: str,
        identifier: str,
        path: Optional[str] = None,
        icon: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort: int = 0,
        type: str = "link",
        target: str = "_self",
        permission: Optional[str] = None,
        is_public: bool = True,
        source: str = "system",
        tenant_id: Optional[int] = None,
        config: Optional[dict] = None,
    ) -> Menu:
        """创建菜单"""
        # 计算层级
        level = 0
        if parent_id:
            parent = await self.get(parent_id)
            if parent:
                level = parent.level + 1
        
        menu = Menu(
            name=name,
            identifier=identifier,
            path=path,
            icon=icon,
            parent_id=parent_id,
            level=level,
            sort=sort,
            type=type,
            target=target,
            permission=permission,
            is_public=is_public,
            source=source,
            tenant_id=tenant_id,
            config=json.dumps(config) if config else None,
        )
        
        self.db.add(menu)
        await self.db.flush()
        
        # 触发事件
        hooks.emit("menu.create", {"menu_id": menu.id, "identifier": identifier})
        
        return menu
    
    async def get(self, menu_id: int) -> Optional[Menu]:
        """获取菜单"""
        result = await self.db.execute(
            select(Menu).options(selectinload(Menu.children)).where(Menu.id == menu_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_identifier(self, identifier: str) -> Optional[Menu]:
        """根据标识获取菜单"""
        result = await self.db.execute(
            select(Menu).where(Menu.identifier == identifier)
        )
        return result.scalar_one_or_none()
    
    async def get_tree(
        self,
        tenant_id: Optional[int] = None,
        is_public: Optional[bool] = None,
        is_active: Optional[bool] = True,
    ) -> List[Menu]:
        """获取菜单树"""
        query = select(Menu).options(
            selectinload(Menu.children)
        ).where(Menu.parent_id.is_(None))
        
        if tenant_id is not None:
            query = query.where(Menu.tenant_id == tenant_id)
        
        if is_public is not None:
            query = query.where(Menu.is_public == is_public)
        
        if is_active is not None:
            query = query.where(Menu.is_active == is_active)
        
        query = query.order_by(Menu.sort)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_user_menus(
        self,
        user_id: int,
        tenant_id: Optional[int] = None,
    ) -> List[Menu]:
        """获取用户可见菜单"""
        # 获取用户自定义菜单
        user_menu_result = await self.db.execute(
            select(UserMenu).where(
                and_(
                    UserMenu.user_id == user_id,
                    UserMenu.is_visible == True
                )
            )
        )
        user_menus = user_menu_result.scalars().all()
        
        if user_menus:
            menu_ids = [um.menu_id for um in user_menus]
            result = await self.db.execute(
                select(Menu).where(Menu.id.in_(menu_ids)).order_by(Menu.sort)
            )
            return list(result.scalars().all())
        
        # 没有自定义菜单，返回公开菜单
        return await self.get_tree(tenant_id=tenant_id, is_public=True)
    
    async def list(
        self,
        source: Optional[str] = None,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Menu], int]:
        """获取菜单列表"""
        query = select(Menu)
        
        if source:
            query = query.where(Menu.source == source)
        
        if tenant_id is not None:
            query = query.where(Menu.tenant_id == tenant_id)
        
        # 计数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询
        query = query.offset(skip).limit(limit).order_by(Menu.sort, Menu.created_at)
        result = await self.db.execute(query)
        menus = list(result.scalars().all())
        
        return menus, total
    
    async def update(self, menu_id: int, **kwargs) -> Optional[Menu]:
        """更新菜单"""
        menu = await self.get(menu_id)
        if not menu:
            return None
        
        for key, value in kwargs.items():
            if hasattr(menu, key) and key not in ["id", "identifier"]:
                if key == "config" and isinstance(value, dict):
                    value = json.dumps(value)
                setattr(menu, key, value)
        
        # 重新计算层级
        if "parent_id" in kwargs:
            if kwargs["parent_id"]:
                parent = await self.get(kwargs["parent_id"])
                menu.level = parent.level + 1 if parent else 0
            else:
                menu.level = 0
        
        await self.db.flush()
        return menu
    
    async def delete(self, menu_id: int) -> bool:
        """删除菜单"""
        menu = await self.get(menu_id)
        if not menu:
            return False
        
        # 删除子菜单
        for child in menu.children:
            await self.delete(child.id)
        
        await self.db.delete(menu)
        await self.db.flush()
        
        hooks.emit("menu.delete", {"menu_id": menu_id})
        
        return True
    
    # ============ 插件菜单注册 ============
    
    async def register_addon_menu(
        self,
        addon_identifier: str,
        menus: List[dict],
        tenant_id: Optional[int] = None,
    ) -> List[Menu]:
        """为插件注册菜单"""
        created_menus = []
        
        for menu_data in menus:
            identifier = f"{addon_identifier}_{menu_data.get('do', menu_data.get('identifier', 'menu'))}"
            
            # 检查是否已存在
            existing = await self.get_by_identifier(identifier)
            if existing:
                continue
            
            menu = await self.create(
                name=menu_data.get("title", menu_data.get("name", "")),
                identifier=identifier,
                path=menu_data.get("path"),
                icon=menu_data.get("icon"),
                sort=menu_data.get("sort", 0),
                type=menu_data.get("type", "link"),
                permission=menu_data.get("permission"),
                is_public=menu_data.get("is_public", True),
                source=addon_identifier,
                tenant_id=tenant_id,
                config=menu_data.get("config"),
            )
            
            created_menus.append(menu)
        
        return created_menus
    
    async def unregister_addon_menus(self, addon_identifier: str) -> int:
        """注销插件菜单"""
        result = await self.db.execute(
            select(Menu).where(Menu.source == addon_identifier)
        )
        menus = result.scalars().all()
        
        count = 0
        for menu in menus:
            await self.delete(menu.id)
            count += 1
        
        return count
    
    # ============ 用户菜单 ============
    
    async def set_user_menu(
        self,
        user_id: int,
        menu_id: int,
        is_visible: bool = True,
        sort: int = 0,
    ) -> UserMenu:
        """设置用户菜单"""
        result = await self.db.execute(
            select(UserMenu).where(
                and_(
                    UserMenu.user_id == user_id,
                    UserMenu.menu_id == menu_id
                )
            )
        )
        user_menu = result.scalar_one_or_none()
        
        if user_menu:
            user_menu.is_visible = is_visible
            user_menu.sort = sort
        else:
            user_menu = UserMenu(
                user_id=user_id,
                menu_id=menu_id,
                is_visible=is_visible,
                sort=sort
            )
            self.db.add(user_menu)
        
        await self.db.flush()
        return user_menu
    
    async def remove_user_menu(self, user_id: int, menu_id: int) -> bool:
        """移除用户菜单"""
        result = await self.db.execute(
            select(UserMenu).where(
                and_(
                    UserMenu.user_id == user_id,
                    UserMenu.menu_id == menu_id
                )
            )
        )
        user_menu = result.scalar_one_or_none()
        
        if user_menu:
            await self.db.delete(user_menu)
            await self.db.flush()
            return True
        
        return False

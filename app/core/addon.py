"""
插件基类
SCALE OS v10.0

所有插件必须继承此基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Callable
from pathlib import Path
import json


class BaseAddon(ABC):
    """插件基类"""
    
    # 插件元信息（子类必须覆盖）
    name: str = ""                    # 插件名称
    identifier: str = ""              # 插件标识（唯一）
    version: str = "1.0.0"           # 版本号
    author: str = ""                  # 作者
    description: str = ""             # 描述
    type: str = "business"            # 类型: business/customer/activity/services/other
    
    # 插件状态
    _enabled: bool = False
    _installed: bool = False
    _path: Optional[Path] = None
    
    def __init__(self):
        self._hooks: dict[str, list[Callable]] = {}
        self._routes: list = []
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @property
    def installed(self) -> bool:
        return self._installed
    
    @property
    def path(self) -> Optional[Path]:
        return self._path
    
    @classmethod
    def get_manifest(cls) -> dict:
        """获取插件配置清单"""
        return {
            "name": cls.name,
            "identifier": cls.identifier,
            "version": cls.version,
            "author": cls.author,
            "description": cls.description,
            "type": cls.type,
        }
    
    # ============ 生命周期方法 ============
    
    def install(self) -> bool:
        """安装插件"""
        if self._installed:
            return True
        
        # 执行安装逻辑
        result = self._on_install()
        if result:
            self._installed = True
        
        return result
    
    def uninstall(self) -> bool:
        """卸载插件"""
        if not self._installed:
            return True
        
        # 先禁用
        if self._enabled:
            self.disable()
        
        # 执行卸载逻辑
        result = self._on_uninstall()
        if result:
            self._installed = False
        
        return result
    
    def enable(self) -> bool:
        """启用插件"""
        if not self._installed:
            return False
        
        if self._enabled:
            return True
        
        # 执行启用逻辑
        result = self._on_enable()
        if result:
            self._enabled = True
        
        return result
    
    def disable(self) -> bool:
        """禁用插件"""
        if not self._enabled:
            return True
        
        # 执行禁用逻辑
        result = self._on_disable()
        if result:
            self._enabled = False
        
        return result
    
    def upgrade(self, old_version: str) -> bool:
        """升级插件"""
        return self._on_upgrade(old_version)
    
    # ============ 子类可覆盖的生命周期钩子 ============
    
    def _on_install(self) -> bool:
        """安装时执行（子类可覆盖）"""
        return True
    
    def _on_uninstall(self) -> bool:
        """卸载时执行（子类可覆盖）"""
        return True
    
    def _on_enable(self) -> bool:
        """启用时执行（子类可覆盖）"""
        return True
    
    def _on_disable(self) -> bool:
        """禁用时执行（子类可覆盖）"""
        return True
    
    def _on_upgrade(self, old_version: str) -> bool:
        """升级时执行（子类可覆盖）"""
        return True
    
    # ============ 钩子注册 ============
    
    def register_hook(self, event: str, callback: Callable, priority: int = 10):
        """注册钩子监听器"""
        if event not in self._hooks:
            self._hooks[event] = []
        
        self._hooks[event].append({
            "callback": callback,
            "priority": priority,
        })
        
        # 按优先级排序
        self._hooks[event].sort(key=lambda x: x["priority"])
    
    def get_hooks(self, event: str) -> list[Callable]:
        """获取指定事件的所有钩子"""
        if event not in self._hooks:
            return []
        return [h["callback"] for h in self._hooks[event]]
    
    # ============ 路由注册 ============
    
    def register_route(self, path: str, method: str, handler: Callable, **kwargs):
        """注册路由"""
        self._routes.append({
            "path": path,
            "method": method,
            "handler": handler,
            "kwargs": kwargs,
        })
    
    def get_routes(self) -> list:
        """获取所有路由"""
        return self._routes
    
    # ============ 抽象方法（子类必须实现） ============
    
    @abstractmethod
    def get_info(self) -> dict:
        """返回插件详细信息"""
        pass


class AddonInfo:
    """插件信息模型"""
    
    def __init__(
        self,
        identifier: str,
        name: str,
        version: str,
        author: str = "",
        description: str = "",
        type: str = "business",
        enabled: bool = False,
        installed: bool = False,
    ):
        self.identifier = identifier
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.type = type
        self.enabled = enabled
        self.installed = installed
    
    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "type": self.type,
            "enabled": self.enabled,
            "installed": self.installed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AddonInfo":
        return cls(
            identifier=data.get("identifier", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            description=data.get("description", ""),
            type=data.get("type", "business"),
            enabled=data.get("enabled", False),
            installed=data.get("installed", False),
        )

"""
插件加载器
SCALE OS v10.0

负责扫描、加载、管理插件
"""

from typing import Optional, Type, Dict, List
from pathlib import Path
import importlib.util
import json
import sys

from app.core.addon import BaseAddon, AddonInfo
from app.core.hook import hooks


class AddonLoader:
    """插件加载器"""
    
    def __init__(self, addons_dir: str = "app/addons"):
        self.addons_dir = Path(addons_dir)
        self._addons: Dict[str, BaseAddon] = {}
        self._addon_classes: Dict[str, Type[BaseAddon]] = {}
    
    def scan(self) -> List[AddonInfo]:
        """扫描插件目录"""
        addons = []
        
        if not self.addons_dir.exists():
            return addons
        
        for addon_path in self.addons_dir.iterdir():
            if not addon_path.is_dir():
                continue
            
            # 检查是否有 manifest.json
            manifest_path = addon_path / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                identifier = manifest.get("identifier", addon_path.name)
                
                addon_info = AddonInfo(
                    identifier=identifier,
                    name=manifest.get("name", identifier),
                    version=manifest.get("version", "1.0.0"),
                    author=manifest.get("author", ""),
                    description=manifest.get("description", ""),
                    type=manifest.get("type", "business"),
                )
                
                addons.append(addon_info)
                
            except Exception as e:
                print(f"Error loading addon {addon_path}: {e}")
        
        return addons
    
    def load(self, identifier: str) -> Optional[BaseAddon]:
        """加载插件"""
        if identifier in self._addons:
            return self._addons[identifier]
        
        addon_path = self.addons_dir / identifier
        if not addon_path.exists():
            return None
        
        # 加载插件模块
        try:
            # 动态导入插件
            init_path = addon_path / "__init__.py"
            if not init_path.exists():
                return None
            
            spec = importlib.util.spec_from_file_location(
                f"app.addons.{identifier}",
                init_path
            )
            
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"app.addons.{identifier}"] = module
            spec.loader.exec_module(module)
            
            # 查找插件类
            addon_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) 
                    and issubclass(attr, BaseAddon) 
                    and attr is not BaseAddon
                ):
                    addon_class = attr
                    break
            
            if addon_class is None:
                return None
            
            # 实例化插件
            addon = addon_class()
            addon._path = addon_path
            
            # 加载 manifest
            manifest_path = addon_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                addon._installed = manifest.get("installed", False)
                addon._enabled = manifest.get("enabled", False)
            
            # 注册钩子
            self._register_hooks(addon)
            
            self._addons[identifier] = addon
            self._addon_classes[identifier] = addon_class
            
            return addon
            
        except Exception as e:
            print(f"Error loading addon {identifier}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def unload(self, identifier: str) -> bool:
        """卸载插件"""
        if identifier not in self._addons:
            return True
        
        addon = self._addons[identifier]
        
        # 禁用插件
        if addon.enabled:
            addon.disable()
        
        # 清除钩子
        hooks.clear(source=identifier)
        
        # 移除缓存
        del self._addons[identifier]
        if identifier in self._addon_classes:
            del self._addon_classes[identifier]
        
        return True
    
    def install(self, identifier: str) -> bool:
        """安装插件"""
        addon = self.load(identifier)
        if addon is None:
            return False
        
        if addon.installed:
            return True
        
        # 执行安装
        if addon.install():
            # 更新 manifest
            self._update_manifest(identifier, {"installed": True})
            # 触发事件
            hooks.emit("addon.install", {"identifier": identifier})
            return True
        
        return False
    
    def uninstall(self, identifier: str) -> bool:
        """卸载插件"""
        addon = self._addons.get(identifier)
        if addon is None:
            return True
        
        # 执行卸载
        if addon.uninstall():
            # 更新 manifest
            self._update_manifest(identifier, {"installed": False, "enabled": False})
            # 触发事件
            hooks.emit("addon.uninstall", {"identifier": identifier})
            return True
        
        return False
    
    def enable(self, identifier: str) -> bool:
        """启用插件"""
        addon = self._addons.get(identifier)
        if addon is None:
            addon = self.load(identifier)
        
        if addon is None:
            return False
        
        if not addon.installed:
            return False
        
        if addon.enable():
            self._update_manifest(identifier, {"enabled": True})
            hooks.emit("addon.enable", {"identifier": identifier})
            return True
        
        return False
    
    def disable(self, identifier: str) -> bool:
        """禁用插件"""
        addon = self._addons.get(identifier)
        if addon is None:
            return True
        
        if addon.disable():
            self._update_manifest(identifier, {"enabled": False})
            hooks.emit("addon.disable", {"identifier": identifier})
            return True
        
        return False
    
    def get_addon(self, identifier: str) -> Optional[BaseAddon]:
        """获取插件实例"""
        return self._addons.get(identifier)
    
    def get_all_addons(self) -> Dict[str, BaseAddon]:
        """获取所有已加载的插件"""
        return self._addons.copy()
    
    def _register_hooks(self, addon: BaseAddon):
        """注册插件的钩子"""
        # 查找插件中定义的钩子
        if hasattr(addon, "hooks"):
            for event, callbacks in addon.hooks.items():
                for cb in callbacks if isinstance(cb, list) else [cb]:
                    hooks.subscribe(event, cb, source=addon.identifier)
        
        if hasattr(addon, "handlers"):
            for event, callbacks in addon.handlers.items():
                for cb in callbacks if isinstance(cb, list) else [cb]:
                    hooks.handle(event, cb, source=addon.identifier)
    
    def _update_manifest(self, identifier: str, updates: dict):
        """更新插件配置"""
        addon_path = self.addons_dir / identifier
        manifest_path = addon_path / "manifest.json"
        
        if not manifest_path.exists():
            return
        
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            manifest.update(updates)
            
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error updating manifest: {e}")


# 全局插件加载器实例
addon_loader = AddonLoader()

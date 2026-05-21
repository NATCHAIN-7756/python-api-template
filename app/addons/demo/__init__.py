"""
演示插件
SCALE OS v10.0
"""

from typing import Any

from app.core.addon import BaseAddon
from app.core.hook import Event, on_event, handle_event


class DemoAddon(BaseAddon):
    """演示插件"""
    
    name = "演示插件"
    identifier = "demo"
    version = "1.0.0"
    author = "SCALE OS"
    description = "演示插件功能"
    type = "business"
    
    def get_info(self) -> dict:
        return {
            "name": self.name,
            "identifier": self.identifier,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "enabled": self.enabled,
            "installed": self.installed,
        }
    
    def _on_install(self) -> bool:
        """安装时执行"""
        print(f"[DemoAddon] 安装插件 {self.identifier}")
        # 这里可以创建数据库表、初始化数据等
        return True
    
    def _on_uninstall(self) -> bool:
        """卸载时执行"""
        print(f"[DemoAddon] 卸载插件 {self.identifier}")
        # 这里可以清理数据库表、删除数据等
        return True
    
    def _on_enable(self) -> bool:
        """启用时执行"""
        print(f"[DemoAddon] 启用插件 {self.identifier}")
        # 注册钩子
        self._register_hooks()
        return True
    
    def _on_disable(self) -> bool:
        """禁用时执行"""
        print(f"[DemoAddon] 禁用插件 {self.identifier}")
        return True
    
    def _register_hooks(self):
        """注册钩子监听器"""
        from app.core.hook import hooks
        
        # 订阅用户注册事件
        hooks.subscribe("user.register", self.on_user_register, source=self.identifier)
        
        # 订阅帖子创建事件
        hooks.subscribe("post.create", self.on_post_create, source=self.identifier)
        
        # 注册自定义事件处理器
        hooks.handle("custom.demo", self.handle_demo, source=self.identifier)
    
    def on_user_register(self, event: Event):
        """用户注册时触发"""
        print(f"[DemoAddon] 新用户注册: {event.data}")
        # 可以在这里发送欢迎消息、记录日志等
    
    def on_post_create(self, event: Event):
        """帖子创建时触发"""
        print(f"[DemoAddon] 新帖子创建: {event.data}")
        # 可以在这里发送通知、更新统计等
    
    def handle_demo(self, event: Event) -> Any:
        """处理自定义事件"""
        print(f"[DemoAddon] 处理自定义事件: {event.data}")
        return {"status": "ok", "message": "Demo handled"}


# 导出插件实例
addon = DemoAddon()

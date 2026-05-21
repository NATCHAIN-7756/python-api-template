"""
Models
SCALE OS v10.0
"""

from app.models.user import User
from app.models.user_group import UserGroup
from app.models.user_profile import UserProfile
from app.models.user_points import UserPoints, PointsLog
from app.models.user_level import UserLevel, UserOnline
from app.models.permission import Permission, GroupPermission
from app.models.category import Category
from app.models.post import Post, PostStatus, PostType
from app.models.comment import Comment
from app.models.tag import Tag, PostTag
from app.models.like import Like, Favorite
from app.models.follow import Follow, Friend
from app.models.message import Message, Notification
from app.models.file import File, FileConfig
from app.models.search import SearchIndex, SearchHistory, HotSearch
from app.models.tenant import Tenant, TenantConfig, TenantAddon, TenantUser, TenantDomain
from app.models.menu import Menu, MenuItem, UserMenu

__all__ = [
    "User",
    "UserGroup",
    "UserProfile",
    "UserPoints",
    "PointsLog",
    "UserLevel",
    "UserOnline",
    "Permission",
    "GroupPermission",
    "Category",
    "Post",
    "PostStatus",
    "PostType",
    "Comment",
    "Tag",
    "PostTag",
    "Like",
    "Favorite",
    "Follow",
    "Friend",
    "Message",
    "Notification",
    "File",
    "FileConfig",
    "SearchIndex",
    "SearchHistory",
    "HotSearch",
    "Tenant",
    "TenantConfig",
    "TenantAddon",
    "TenantUser",
    "TenantDomain",
    "Menu",
    "MenuItem",
    "UserMenu",
]
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

__all__ = [
    # User
    "User",
    # UserGroup
    "UserGroup",
    # UserProfile
    "UserProfile",
    # UserPoints
    "UserPoints",
    "PointsLog",
    # UserLevel
    "UserLevel",
    "UserOnline",
    # Permission
    "Permission",
    "GroupPermission",
    # Content
    "Category",
    "Post",
    "PostStatus",
    "PostType",
    "Comment",
    "Tag",
    "PostTag",
]
"""
Services
SCALE OS v10.0
"""

from app.services.user import UserService
from app.services.user_group import UserGroupService
from app.services.user_profile import UserProfileService
from app.services.user_points import UserPointsService, UserLevelService
from app.services.category import CategoryService
from app.services.post import PostService
from app.services.comment import CommentService
from app.services.tag import TagService

__all__ = [
    "UserService",
    "UserGroupService",
    "UserProfileService",
    "UserPointsService",
    "UserLevelService",
    "CategoryService",
    "PostService",
    "CommentService",
    "TagService",
]
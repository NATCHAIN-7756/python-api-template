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
from app.services.like import LikeService, FavoriteService
from app.services.follow import FollowService, FriendService
from app.services.message import MessageService, NotificationService
from app.services.file import FileService
from app.services.search import SearchService

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
    "LikeService",
    "FavoriteService",
    "FollowService",
    "FriendService",
    "MessageService",
    "NotificationService",
    "FileService",
    "SearchService",
]
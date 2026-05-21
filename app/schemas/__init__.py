"""
Schemas
SCALE OS v10.0
"""

from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, Token
)
from app.schemas.user_group import (
    UserGroupBase, UserGroupCreate, UserGroupUpdate, UserGroupResponse,
    PermissionBase, PermissionCreate, PermissionResponse
)
from app.schemas.user_profile import (
    UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse
)
from app.schemas.user_points import (
    UserPointsBase, UserPointsResponse, PointsLogCreate, PointsLogResponse,
    UserLevelBase, UserLevelCreate, UserLevelResponse
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserListResponse", "Token",
    # UserGroup
    "UserGroupBase", "UserGroupCreate", "UserGroupUpdate", "UserGroupResponse",
    "PermissionBase", "PermissionCreate", "PermissionResponse",
    # UserProfile
    "UserProfileBase", "UserProfileCreate", "UserProfileUpdate", "UserProfileResponse",
    # UserPoints
    "UserPointsBase", "UserPointsResponse", "PointsLogCreate", "PointsLogResponse",
    "UserLevelBase", "UserLevelCreate", "UserLevelResponse",
]
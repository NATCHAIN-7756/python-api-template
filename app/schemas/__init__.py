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
from app.schemas.category import (
    CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse, CategorySimple
)
from app.schemas.post import (
    PostBase, PostCreate, PostUpdate, PostResponse, PostDetailResponse, PostListResponse
)
from app.schemas.comment import (
    CommentBase, CommentCreate, CommentUpdate, CommentResponse, CommentDetailResponse, CommentListResponse
)
from app.schemas.tag import (
    TagBase, TagCreate, TagUpdate, TagResponse, TagSimple
)
from app.schemas.file import (
    FileResponse, FileListResponse, FileUpdate, UploadResponse, FileStats
)
from app.schemas.search import (
    SearchResponse, SearchResult, SearchHistoryResponse, HotSearchResponse
)
from app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse, TenantDetailResponse,
    TenantAddonResponse, TenantUserResponse
)
from app.schemas.menu import (
    MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse,
    MenuItemResponse, UserMenuResponse
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
    # Category
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse", "CategoryTreeResponse", "CategorySimple",
    # Post
    "PostBase", "PostCreate", "PostUpdate", "PostResponse", "PostDetailResponse", "PostListResponse",
    # Comment
    "CommentBase", "CommentCreate", "CommentUpdate", "CommentResponse", "CommentDetailResponse", "CommentListResponse",
    # Tag
    "TagBase", "TagCreate", "TagUpdate", "TagResponse", "TagSimple",
    # File
    "FileResponse", "FileListResponse", "FileUpdate", "UploadResponse", "FileStats",
    # Search
    "SearchResponse", "SearchResult", "SearchHistoryResponse", "HotSearchResponse",
    # Tenant
    "TenantCreate", "TenantUpdate", "TenantResponse", "TenantDetailResponse",
    "TenantAddonResponse", "TenantUserResponse",
    # Menu
    "MenuCreate", "MenuUpdate", "MenuResponse", "MenuTreeResponse",
    "MenuItemResponse", "UserMenuResponse",
]
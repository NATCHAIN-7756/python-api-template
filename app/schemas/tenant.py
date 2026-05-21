"""
租户 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    """租户基础"""
    name: str = Field(..., min_length=1, max_length=100)
    identifier: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")
    type: str = Field(default="website")


class TenantCreate(TenantBase):
    """创建租户"""
    appid: Optional[str] = None
    appsecret: Optional[str] = None
    token: Optional[str] = None
    config: Optional[dict] = None


class TenantUpdate(BaseModel):
    """更新租户"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    appid: Optional[str] = None
    appsecret: Optional[str] = None
    token: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    """租户响应"""
    id: int
    name: str
    identifier: str
    type: str
    is_active: bool
    is_verified: bool
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantDetailResponse(TenantResponse):
    """租户详情"""
    appid: Optional[str] = None
    config: Optional[dict] = None
    expires_at: Optional[datetime] = None


class TenantAddonResponse(BaseModel):
    """租户插件响应"""
    id: int
    tenant_id: int
    addon_identifier: str
    is_enabled: bool
    config: Optional[dict] = None
    
    class Config:
        from_attributes = True


class TenantUserResponse(BaseModel):
    """租户用户响应"""
    id: int
    tenant_id: int
    user_id: int
    role: str
    permissions: Optional[list] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

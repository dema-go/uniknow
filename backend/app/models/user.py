"""用户模型"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员 - 不需要审批
    AGENT = "agent"  # 维护员 - 需要审批
    USER = "user"    # 普通用户 - 只读


class User(BaseModel):
    """用户模型"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    tenant_id: str = Field(..., description="租户ID")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    created_at: Optional[str] = Field(None, description="创建时间")


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: str = Field(..., description="用户ID")
    tenant_id: str = Field(..., description="租户ID")
    role: UserRole = Field(..., description="用户角色")

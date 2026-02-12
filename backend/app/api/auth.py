"""认证相关API"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.models.user import TokenData, UserRole
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_info: dict


# 模拟用户数据库（生产环境应该从真实数据库查询）
MOCK_USERS = {
    "admin": {
        "id": "admin_001",
        "username": "admin",
        "password": "admin123",  # 生产环境应该使用哈希密码
        "role": UserRole.ADMIN,
        "tenant_id": "default_tenant"
    },
    "agent": {
        "id": "agent_001",
        "username": "agent",
        "password": "agent123",
        "role": UserRole.AGENT,
        "tenant_id": "default_tenant"
    },
    "user": {
        "id": "user_001",
        "username": "user",
        "password": "user123",
        "role": UserRole.USER,
        "tenant_id": "default_tenant"
    }
}


@router.post("/login")
async def login(request_data: LoginRequest):
    """用户登录

    Args:
        request_data: 登录请求数据

    Returns:
        包含access_token的响应

    Raises:
        HTTPException: 用户名或密码错误
    """
    # 验证用户
    user = MOCK_USERS.get(request_data.username)
    if not user or user["password"] != request_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 创建JWT token
    token_data = {
        "user_id": user["id"],
        "tenant_id": user["tenant_id"],
        "role": user["role"].value
    }
    access_token = create_access_token(token_data)

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"].value,
                "tenantId": user["tenant_id"]
            }
        }
    }


@router.post("/logout")
async def logout():
    """用户登出"""
    # JWT是无状态的，登出主要由前端处理（删除token）
    return {
        "code": 200,
        "message": "登出成功"
    }

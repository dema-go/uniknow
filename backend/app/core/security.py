from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """获取当前登录用户"""
    # TODO: 实现实际的 JWT 验证逻辑
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token


async def verify_tenant(tenant_id: str) -> bool:
    """验证租户权限"""
    # TODO: 实现实际的租户验证逻辑
    return True

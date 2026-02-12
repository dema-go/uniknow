"""安全认证相关"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import TokenData, UserRole


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌

    Args:
        data: 要编码的数据（user_id, tenant_id, role）
        expires_delta: 过期时间增量

    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """解码访问令牌

    Args:
        token: JWT令牌字符串

    Returns:
        TokenData对象

    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        tenant_id: str = payload.get("tenant_id")
        role: str = payload.get("role", UserRole.USER)

        if user_id is None or tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id, tenant_id=tenant_id, role=UserRole(role))

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """获取当前登录用户

    Args:
        credentials: HTTP Bearer认证凭据

    Returns:
        TokenData对象

    Raises:
        HTTPException: 令牌无效
    """
    token = credentials.credentials
    return decode_access_token(token)


async def verify_tenant(tenant_id: str) -> bool:
    """验证租户权限

    Args:
        tenant_id: 租户ID

    Returns:
        验证结果
    """
    # TODO: 实现实际的租户验证逻辑
    return True

"""基于角色的访问控制（RBAC）"""
from functools import wraps
from typing import Callable, List

from fastapi import HTTPException, status

from app.models.user import TokenData, UserRole


def require_role(*allowed_roles: UserRole) -> Callable:
    """要求特定角色才能访问的装饰器

    Args:
        *allowed_roles: 允许的角色列表

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: TokenData, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def skip_approval_for_admin(role: UserRole) -> bool:
    """管理员是否可以跳过审批

    Args:
        role: 用户角色

    Returns:
        是否跳过审批
    """
    return role == UserRole.ADMIN


def can_approve(role: UserRole) -> bool:
    """是否有审批权限

    Args:
        role: 用户角色

    Returns:
        是否有审批权限
    """
    return role in [UserRole.ADMIN, UserRole.AGENT]


def can_edit_case(role: UserRole) -> bool:
    """是否可以编辑案例

    Args:
        role: 用户角色

    Returns:
        是否可以编辑
    """
    return role in [UserRole.ADMIN, UserRole.AGENT]

"""审批相关API"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.models.approval import ApprovalStatus
from app.models.user import TokenData
from app.schemas.common import BaseResponse
from app.core.security import get_current_user
from app.core.rbac import require_role, UserRole
from app.services.approval_service import ApprovalService


router = APIRouter(prefix="/approvals", tags=["审批管理"])


class ApprovalRequest(BaseModel):
    """审批请求"""
    case_id: str = Field(..., description="案例ID")


class ApprovalActionRequest(BaseModel):
    """审批操作请求"""
    comment: Optional[str] = Field(None, description="审批意见")


@router.get("", response_model=BaseResponse)
async def list_approvals(
    status: Optional[ApprovalStatus] = Query(None, description="审批状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: TokenData = Depends(get_current_user),
):
    """获取审批列表

    Args:
        status: 审批状态筛选
        page: 页码
        page_size: 每页数量
        current_user: 当前用户

    Returns:
        审批列表
    """
    service = ApprovalService()
    skip = (page - 1) * page_size

    approvals = await service.list_approvals(
        tenant_id=current_user.tenant_id,
        status=status,
        skip=skip,
        limit=page_size,
    )

    return BaseResponse(
        data={
            "items": approvals,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("", response_model=BaseResponse)
async def create_approval(
    request: ApprovalRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """创建审批请求

    Args:
        request: 审批请求
        current_user: 当前用户

    Returns:
        创建的审批ID
    """
    service = ApprovalService()
    approval = await service.create_approval(
        case_id=request.case_id,
        requester_id=current_user.user_id,
    )

    return BaseResponse(
        message="审批请求已创建",
        data={"id": approval.id}
    )


@router.get("/{approval_id}", response_model=BaseResponse)
async def get_approval(
    approval_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """获取审批详情

    Args:
        approval_id: 审批ID
        current_user: 当前用户

    Returns:
        审批详情
    """
    # 这里需要实现根据ID获取单个审批的逻辑
    # 暂时返回基本响应
    return BaseResponse(
        data={
            "id": approval_id,
            "message": "获取审批详情"
        }
    )


@router.post("/{approval_id}/approve", response_model=BaseResponse)
async def approve_case(
    approval_id: str,
    request: ApprovalActionRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """通过审批

    Args:
        approval_id: 审批ID
        request: 审批操作请求
        current_user: 当前用户

    Returns:
        操作结果
    """
    service = ApprovalService()
    approval = await service.approve(
        approval_id=approval_id,
        approver_id=current_user.user_id,
        comment=request.comment,
    )

    return BaseResponse(
        message="审批通过",
        data={"id": approval.id, "status": approval.status}
    )


@router.post("/{approval_id}/reject", response_model=BaseResponse)
async def reject_case(
    approval_id: str,
    request: ApprovalActionRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """拒绝审批

    Args:
        approval_id: 审批ID
        request: 审批操作请求
        current_user: 当前用户

    Returns:
        操作结果
    """
    service = ApprovalService()
    approval = await service.reject(
        approval_id=approval_id,
        approver_id=current_user.user_id,
        comment=request.comment,
    )

    return BaseResponse(
        message="审批已拒绝",
        data={"id": approval.id, "status": approval.status}
    )

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.case import ApprovalCreate, ApprovalResponse
from app.schemas.common import BaseResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/approvals", tags=["审批管理"])


@router.post("", response_model=BaseResponse)
async def create_approval(
    approval_data: ApprovalCreate,
    approver_id: str = Depends(get_current_user)
):
    """创建审批请求"""
    # TODO: 实现审批创建逻辑
    return BaseResponse(data={"id": "approval_id"})


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str):
    """获取审批详情"""
    # TODO: 实现审批查询逻辑
    return {
        "id": approval_id,
        "case_id": "case_id",
        "approver_id": "approver_id",
        "status": "pending",
        "comment": None,
        "created_at": "2024-01-01T00:00:00",
        "processed_at": None
    }


@router.post("/{approval_id}/approve", response_model=BaseResponse)
async def approve_case(
    approval_id: str,
    comment: str = None,
    approver_id: str = Depends(get_current_user)
):
    """通过审批"""
    # TODO: 实现审批通过逻辑
    return BaseResponse(message="审批通过")


@router.post("/{approval_id}/reject", response_model=BaseResponse)
async def reject_case(
    approval_id: str,
    comment: str = None,
    approver_id: str = Depends(get_current_user)
):
    """拒绝审批"""
    # TODO: 实现审批拒绝逻辑
    return BaseResponse(message="审批已拒绝")

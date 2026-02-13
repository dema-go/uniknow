from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from bson import ObjectId

from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseSearchRequest
)
from app.schemas.common import (
    PaginatedResponse,
    BaseResponse
)
from app.models.user import TokenData
from app.core.security import get_current_user
from app.core.rbac import skip_approval_for_admin, can_edit_case, can_approve
from app.models.user import UserRole
from app.services.case_service import CaseService
from app.services.approval_service import ApprovalService
from app.models.database import CaseStatus

router = APIRouter(prefix="/cases", tags=["案例管理"])


@router.post("", response_model=BaseResponse)
async def create_case(
    case_data: CaseCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """创建案例

    管理员直接发布，维护员需要审批，普通用户无权限
    """
    # 权限检查：只有 Admin 和 Agent 可以创建案例
    if current_user.role == UserRole.USER:
        raise HTTPException(status_code=403, detail="权限不足：普通用户无法创建案例")

    case_service = CaseService()

    # 准备案例数据
    case_dict = {
        **case_data.model_dump(),
        "creator_id": current_user.user_id,
        "tenant_id": current_user.tenant_id,
    }

    # 只有当 status 未设置时才根据角色决定默认状态
    # 如果前端明确传递了 status（如 draft），则使用前端传递的值
    if "status" not in case_dict or not case_dict["status"]:
        if skip_approval_for_admin(current_user.role):
            case_dict["status"] = CaseStatus.PUBLISHED
        else:
            case_dict["status"] = CaseStatus.PENDING_APPROVAL

    case = await case_service.create_case(case_dict)

    # 根据实际状态返回不同消息
    status_messages = {
        CaseStatus.DRAFT: "草稿保存成功",
        CaseStatus.PUBLISHED: "案例发布成功",
        CaseStatus.PENDING_APPROVAL: "案例已提交审批",
    }
    message = status_messages.get(case.status, "操作成功")

    return BaseResponse(
        message=message,
        data={"id": case.id, "status": case.status}
    )


@router.get("/{case_id}", response_model=BaseResponse)
async def get_case(case_id: str):
    """获取案例详情"""
    case_service = CaseService()
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 增加浏览量
    await case_service.increment_view(case_id)

    return BaseResponse(data=case.model_dump())


@router.put("/{case_id}", response_model=BaseResponse)
async def update_case(
    case_id: str,
    case_data: CaseUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """更新案例"""
    # 权限检查：只有 Admin 和 Agent 可以更新案例
    if not can_edit_case(current_user.role):
        raise HTTPException(status_code=403, detail="权限不足：无法编辑案例")

    case_service = CaseService()
    case = await case_service.update_case(case_id, case_data.model_dump(exclude_unset=True))
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return BaseResponse(data={"id": case.id})


@router.delete("/{case_id}", response_model=BaseResponse)
async def delete_case(
    case_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """删除案例"""
    # 权限检查：只有 Admin 可以删除案例
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足：只有管理员可以删除案例")

    case_service = CaseService()
    success = await case_service.delete_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail="案例不存在")
    return BaseResponse(message="删除成功")


@router.get("")
async def list_cases(
    category_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(get_current_user),
):
    """查询案例列表"""
    case_service = CaseService()
    result = await case_service.list_cases(
        tenant_id=current_user.tenant_id,
        category_id=category_id,
        status=status,
        page=page,
        page_size=page_size
    )
    # 统一返回 BaseResponse 格式
    return BaseResponse(data=result)


class ApprovalActionRequest(BaseModel):
    """审批操作请求"""
    comment: Optional[str] = Field(None, description="审批意见")


@router.post("/{case_id}/approve", response_model=BaseResponse)
async def approve_case_by_id(
    case_id: str,
    request: ApprovalActionRequest = ApprovalActionRequest(),
    current_user: TokenData = Depends(get_current_user),
):
    """通过案例审批

    Args:
        case_id: 案例ID
        request: 审批操作请求
        current_user: 当前用户

    Returns:
        操作结果
    """
    # 权限检查：只有 Admin 可以审批案例
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足：只有管理员可以审批案例")

    case_service = CaseService()
    approval_service = ApprovalService()

    # 检查案例是否存在
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查案例状态
    if case.status != CaseStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="案例不在待审批状态")

    # 查找或创建审批记录
    approvals = await approval_service.list_approvals(
        tenant_id=current_user.tenant_id,
        skip=0,
        limit=1,
    )

    approval = None
    for app in approvals:
        if app.get("case_id") == case_id:
            approval = app
            break

    if not approval:
        # 创建审批记录
        approval = await approval_service.create_approval(
            case_id=case_id,
            requester_id=case.creator_id or current_user.user_id,
        )

    # 执行审批
    updated_approval = await approval_service.approve(
        approval_id=approval.id if hasattr(approval, 'id') else str(approval["_id"]),
        approver_id=current_user.user_id,
        comment=request.comment,
    )

    return BaseResponse(
        message="审批通过",
        data={"id": case_id, "approval_id": updated_approval.id, "status": "approved"}
    )


@router.post("/{case_id}/reject", response_model=BaseResponse)
async def reject_case_by_id(
    case_id: str,
    request: ApprovalActionRequest = ApprovalActionRequest(),
    current_user: TokenData = Depends(get_current_user),
):
    """拒绝案例审批

    Args:
        case_id: 案例ID
        request: 审批操作请求
        current_user: 当前用户

    Returns:
        操作结果
    """
    # 权限检查：只有 Admin 可以拒绝案例
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足：只有管理员可以拒绝案例")

    case_service = CaseService()
    approval_service = ApprovalService()

    # 检查案例是否存在
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查案例状态
    if case.status != CaseStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="案例不在待审批状态")

    # 查找或创建审批记录
    approvals = await approval_service.list_approvals(
        tenant_id=current_user.tenant_id,
        skip=0,
        limit=100,
    )

    approval = None
    for app in approvals:
        if app.get("case_id") == case_id:
            approval = app
            break

    if not approval:
        # 创建审批记录
        approval = await approval_service.create_approval(
            case_id=case_id,
            requester_id=case.creator_id or current_user.user_id,
        )

    # 执行拒绝
    updated_approval = await approval_service.reject(
        approval_id=approval.id if hasattr(approval, 'id') else str(approval["_id"]),
        approver_id=current_user.user_id,
        comment=request.comment,
    )

    return BaseResponse(
        message="审批已拒绝",
        data={"id": case_id, "approval_id": updated_approval.id, "status": "rejected"}
    )

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.core.rbac import skip_approval_for_admin
from app.services.case_service import CaseService
from app.models.database import CaseStatus

router = APIRouter(prefix="/cases", tags=["案例管理"])


@router.post("", response_model=BaseResponse)
async def create_case(
    case_data: CaseCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """创建案例

    管理员直接发布，维护员需要审批
    """
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


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str):
    """获取案例详情"""
    case_service = CaseService()
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 增加浏览量
    await case_service.increment_view(case_id)

    return case


@router.put("/{case_id}", response_model=BaseResponse)
async def update_case(
    case_id: str,
    case_data: CaseUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """更新案例"""
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

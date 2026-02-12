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
from app.core.security import get_current_user
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["案例管理"])


@router.post("", response_model=BaseResponse)
async def create_case(
    case_data: CaseCreate,
    user_id: str = Depends(get_current_user)
):
    """创建案例"""
    case_service = CaseService()
    case = await case_service.create_case({
        **case_data.model_dump(),
        "creator_id": user_id
    })
    return BaseResponse(data={"id": case.id})


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str):
    """获取案例详情"""
    case_service = CaseService()
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return case


@router.put("/{case_id}", response_model=BaseResponse)
async def update_case(
    case_id: str,
    case_data: CaseUpdate
):
    """更新案例"""
    case_service = CaseService()
    case = await case_service.update_case(case_id, case_data.model_dump(exclude_unset=True))
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return BaseResponse(data={"id": case.id})


@router.delete("/{case_id}", response_model=BaseResponse)
async def delete_case(case_id: str):
    """删除案例"""
    case_service = CaseService()
    success = await case_service.delete_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail="案例不存在")
    return BaseResponse(message="删除成功")


@router.get("", response_model=PaginatedResponse[CaseResponse])
async def list_cases(
    category_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: str = Depends(get_current_user)
):
    """查询案例列表"""
    case_service = CaseService()
    result = await case_service.list_cases(
        tenant_id=tenant_id,
        category_id=category_id,
        status=status,
        page=page,
        page_size=page_size
    )
    return result

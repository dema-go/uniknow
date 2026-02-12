from fastapi import APIRouter, Depends, Query

from app.schemas.case import CaseSearchRequest
from app.schemas.common import BaseResponse
from app.services.search_service import SearchService
from app.core.security import get_current_user

router = APIRouter(prefix="/search", tags=["案例搜索"])


@router.post("/cases", response_model=dict)
async def search_cases(
    search_request: CaseSearchRequest,
    tenant_id: str = Depends(get_current_user)
):
    """坐席搜索案例"""
    search_service = SearchService()
    result = await search_service.search_cases(
        query=search_request.query,
        tenant_id=tenant_id,
        category_id=search_request.category_id,
        case_type=search_request.case_type,
        tags=search_request.tags,
        page=search_request.page,
        page_size=search_request.page_size
    )
    return result


@router.get("/user", response_model=dict)
async def user_search(
    q: str = Query(..., min_length=1),
    tenant_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """用户搜索（仅对外案例）"""
    search_service = SearchService()
    result = await search_service.user_search(
        query=q,
        tenant_id=tenant_id,
        page=page,
        page_size=page_size
    )
    return result

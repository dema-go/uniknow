from typing import Optional

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from app.schemas.common import BaseResponse
from app.models.user import TokenData
from app.core.security import get_current_user
from app.services.case_service import CaseService


router = APIRouter(prefix="/operation", tags=["运营统计"])


@router.get("/stats/case")
async def get_case_stats(current_user: TokenData = Depends(get_current_user)):
    """获取案例统计"""
    case_service = CaseService()
    stats = await case_service.get_statistics(current_user.tenant_id)

    # 计算今日浏览量（简化实现，实际应从logs表统计）
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 这里使用简化实现，实际应该查询操作日志
    today_views = stats.get("total_views", 0) // 10  # 简化假设今日浏览量为总量的10%

    # 转换为前端期望的驼峰命名格式
    formatted_stats = {
        "totalCases": stats.get("total_cases", 0),
        "internalCases": stats.get("internal_cases", 0),
        "externalCases": stats.get("external_cases", 0),
        "pendingApproval": stats.get("pending_approval", 0),
        "todayViews": today_views,
        "likes": stats.get("total_likes", 0),
        "totalViews": stats.get("total_views", 0)
    }

    return BaseResponse(data=formatted_stats)


@router.get("/stats/qa")
async def get_qa_stats(current_user: TokenData = Depends(get_current_user)):
    """获取问答统计"""
    # TODO: 从问答记录表统计真实数据
    # 目前返回模拟数据
    return BaseResponse(data={
        "total_questions": 1000,
        "answered": 850,
        "ai_resolved": 700,
        "ai_resolution_rate": 0.82,
        "avg_response_time": 2.5
    })


@router.get("/recent-cases")
async def get_recent_cases(
    limit: int = Query(5, ge=1, le=20),
    current_user: TokenData = Depends(get_current_user)
):
    """获取最近案例"""
    case_service = CaseService()
    result = await case_service.list_cases(
        tenant_id=current_user.tenant_id,
        page=1,
        page_size=limit
    )

    # 格式化返回数据
    cases = []
    for case in result.get("items", []):
        cases.append({
            "id": case.id,
            "title": case.title,
            "case_type": case.case_type,
            "status": case.status,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "view_count": case.view_count
        })

    return BaseResponse(data={
        "items": cases,
        "total": result.get("total", 0)
    })


@router.get("/logs")
async def get_operation_logs(
    page: int = 1,
    page_size: int = 50,
    current_user: TokenData = Depends(get_current_user)
):
    """获取操作日志"""
    # TODO: 实现日志查询逻辑
    return BaseResponse(data={
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    })

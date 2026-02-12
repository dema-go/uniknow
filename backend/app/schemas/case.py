from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.database import CaseType, CaseStatus


class CaseCreate(BaseModel):
    """创建案例请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: str
    case_type: CaseType = CaseType.EXTERNAL
    tags: List[str] = []
    template_id: Optional[str] = None


class CaseUpdate(BaseModel):
    """更新案例请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    category_id: Optional[str] = None
    case_type: Optional[CaseType] = None
    tags: Optional[List[str]] = None


class CaseResponse(BaseModel):
    """案例响应"""
    id: str
    tenant_id: str
    title: str
    content: str
    category_id: str
    case_type: str
    status: str
    tags: List[str]
    view_count: int
    like_count: int
    dislike_count: int
    creator_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class CaseSearchRequest(BaseModel):
    """案例搜索请求"""
    query: str = Field(..., min_length=1)
    category_id: Optional[str] = None
    case_type: Optional[CaseType] = None
    tags: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20


class CaseSearchResponse(BaseModel):
    """案例搜索响应"""
    items: List[CaseResponse]
    total: int
    page: int
    page_size: int
    facets: Optional[dict] = None


class ApprovalCreate(BaseModel):
    """创建审批请求"""
    case_id: str
    approver_id: str
    comment: Optional[str] = None


class ApprovalResponse(BaseModel):
    """审批响应"""
    id: str
    case_id: str
    approver_id: str
    status: str
    comment: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime] = None

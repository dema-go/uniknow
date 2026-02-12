"""审批模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(BaseModel):
    """审批模型"""
    id: str = Field(..., description="审批ID")
    case_id: str = Field(..., description="案例ID")
    requester_id: str = Field(..., description="申请人ID")
    approver_id: Optional[str] = Field(None, description="审批人ID")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="审批状态")
    comment: Optional[str] = Field(None, description="审批意见")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    processed_at: Optional[datetime] = Field(None, description="处理时间")


class ApprovalCreate(BaseModel):
    """创建审批请求"""
    case_id: str = Field(..., description="案例ID")


class ApprovalUpdate(BaseModel):
    """更新审批请求"""
    comment: Optional[str] = Field(None, description="审批意见")


class ApprovalResponse(BaseModel):
    """审批响应"""
    id: str
    case_id: str
    case_title: str
    requester_id: str
    requester_name: str
    approver_id: Optional[str]
    approver_name: Optional[str]
    status: ApprovalStatus
    comment: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

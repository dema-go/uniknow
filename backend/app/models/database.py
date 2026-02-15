from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from bson import ObjectId


class CaseType(str, Enum):
    INTERNAL = "internal"      # 对内案例
    EXTERNAL = "external"      # 对外案例


class CaseStatus(str, Enum):
    DRAFT = "draft"            # 草稿
    PENDING_APPROVAL = "pending_approval"  # 待审批
    APPROVED = "approved"      # 已审批
    REJECTED = "rejected"      # 已拒绝
    PUBLISHED = "published"    # 已发布
    ARCHIVED = "archived"      # 已归档


class CaseForm(str, Enum):
    """案例形式"""
    FAQ = "faq"           # FAQ 类型（纯文本）
    DOCUMENT = "document"  # 文档类型（文件上传）


class Case(BaseModel):
    """案例模型"""
    id: Optional[str] = None
    tenant_id: str                     # 租户ID
    title: str                         # 案例标题
    content: str                       # 案例内容（FAQ 内容或文档描述）
    category_id: str                   # 目录ID
    case_type: CaseType = CaseType.EXTERNAL
    case_form: CaseForm = CaseForm.FAQ # 案例形式
    status: CaseStatus = CaseStatus.DRAFT
    tags: List[str] = []
    template_id: Optional[str] = None  # 使用的模板ID
    approval_id: Optional[str] = None  # 审批流程ID

    # 文档相关字段（仅当 case_form=document 时使用）
    file_name: Optional[str] = None    # 原始文件名
    file_path: Optional[str] = None    # MinIO 存储路径
    file_size: Optional[int] = None    # 文件大小（字节）
    file_type: Optional[str] = None    # 文件 MIME 类型

    view_count: int = 0               # 浏览量
    like_count: int = 0                # 点赞数
    dislike_count: int = 0            # 点踩数
    creator_id: str                   # 创建人
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    published_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CaseApproval(BaseModel):
    """案例审批模型"""
    id: Optional[str] = None
    tenant_id: str
    case_id: str
    applicant: str
    approver_id: str                   # 审批人
    status: str = "pending"
    comment: Optional[str] = None
    created_at: datetime = datetime.now()
    processed_at: Optional[datetime] = None


class CaseTemplate(BaseModel):
    """案例模板模型"""
    id: Optional[str] = None
    tenant_id: str
    name: str
    fields: List[dict]                 # 模板字段定义
    is_default: bool = False
    created_by: str
    created_at: datetime = datetime.now()


class OperationLog(BaseModel):
    """操作日志模型"""
    id: Optional[str] = None
    tenant_id: str
    operator_id: str
    operation_type: str
    target_type: str
    target_id: str
    detail: dict
    created_at: datetime = datetime.now()


class UserInteraction(BaseModel):
    """用户交互模型"""
    id: Optional[str] = None
    tenant_id: str
    user_id: str
    case_id: str
    interaction_type: str              # view, like, dislike, search
    query: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime = datetime.now()

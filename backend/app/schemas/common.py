from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class GraphRagResponse(BaseModel):
    """GraphRag 问答响应"""
    answer: str
    sources: list[dict]
    graph_context: Optional[dict] = None
    confidence: float

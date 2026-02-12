from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.database import CaseStatus
from app.tools.embedding import EmbeddingService
import re


class SearchService:
    """搜索服务"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["cases"]

    async def search_cases(
        self,
        query: str,
        tenant_id: str,
        category_id: Optional[str] = None,
        case_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        搜索案例
        使用向量搜索 + 关键词搜索的混合搜索策略
        """
        # 1. 尝试生成查询向量（可选，用于未来的向量搜索）
        try:
            query_vector = await self.embedding_service.embed_query(query)
        except Exception as e:
            # embedding 服务失败时，只使用关键词搜索
            query_vector = None

        # 2. 构建查询条件
        filter_conditions = {
            "tenant_id": tenant_id,
            "status": CaseStatus.PUBLISHED
        }
        if category_id:
            filter_conditions["category_id"] = category_id
        if case_type:
            filter_conditions["case_type"] = case_type
        if tags:
            filter_conditions["tags"] = {"$all": tags}

        # 3. 执行关键词搜索
        results = await self._keyword_search(
            query, filter_conditions, page, page_size
        )

        return results

    async def _keyword_search(
        self,
        query: str,
        filters: dict,
        page: int,
        page_size: int
    ) -> dict:
        """关键词搜索实现"""
        # 构建搜索查询 - 在标题和内容中搜索关键词
        search_query = {
            **filters,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]
        }

        # 如果查询词为空，移除 $or 条件
        if not query or query.strip() == "":
            search_query = filters

        total = await self.collection.count_documents(search_query)
        skip = (page - 1) * page_size

        cursor = self.collection.find(search_query).skip(skip).limit(page_size).sort("created_at", -1)

        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(doc)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }

    async def user_search(
        self,
        query: str,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        用户搜索（只能搜索对外案例）
        """
        return await self.search_cases(
            query=query,
            tenant_id=tenant_id,
            case_type="external",
            page=page,
            page_size=page_size
        )

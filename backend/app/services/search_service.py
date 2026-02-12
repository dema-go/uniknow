from typing import Optional, List
from app.core.config import settings
from app.models.database import CaseStatus
from app.tools.embedding import EmbeddingService


class SearchService:
    """搜索服务"""

    def __init__(self):
        self.embedding_service = EmbeddingService()

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
        # 1. 生成查询向量
        query_vector = await self.embedding_service.embed_query(query)

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

        # 3. 执行向量搜索（这里简化为关键词搜索）
        # TODO: 集成实际的向量数据库（如 Milvus、Pinecone）
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
        """关键词搜索（临时实现）"""
        # TODO: 实现实际的搜索逻辑
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size
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

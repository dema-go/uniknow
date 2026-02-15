from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.database import CaseStatus
from app.tools.embedding import EmbeddingService
from app.services.milvus_service import get_milvus_service, MilvusService
from app.services.rerank_service import get_rerank_service, get_simple_rerank_service
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """混合搜索服务 - 结合关键词搜索、向量搜索和 Rerank"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["cases"]
        self._milvus_service: Optional[MilvusService] = None
        self._rerank_enabled = settings.RERANK_ENABLED

    @property
    def milvus_service(self) -> MilvusService:
        """延迟获取 Milvus 服务"""
        if self._milvus_service is None:
            try:
                self._milvus_service = get_milvus_service()
            except Exception as e:
                logger.warning(f"Failed to get Milvus service: {e}")
        return self._milvus_service

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
        混合搜索案例
        结合关键词搜索、向量搜索，并使用 Rerank 重排序
        """
        # 1. 并行执行关键词搜索和向量搜索
        keyword_results = []
        vector_results = []

        # 关键词搜索
        filter_conditions = self._build_filter_conditions(
            tenant_id, category_id, case_type, tags
        )

        # 执行关键词搜索
        keyword_results = await self._keyword_search_all(
            query, filter_conditions, limit=50
        )

        # 2. 向量搜索（如果 Milvus 可用）
        if self.milvus_service:
            try:
                query_vector = await self.embedding_service.embed_query(query)
                vector_results = await self.milvus_service.search_similar(
                    query_vector=query_vector,
                    tenant_id=tenant_id,
                    top_k=50,
                    case_type=case_type,
                    category_id=category_id
                )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")

        # 3. 合并结果（去重）
        merged_results = self._merge_results(keyword_results, vector_results)

        # 4. Rerank 重排序
        if merged_results:
            try:
                if self._rerank_enabled:
                    rerank_service = get_rerank_service()
                    reranked_results = await rerank_service.rerank(
                        query=query,
                        documents=merged_results,
                        top_k=min(100, len(merged_results))
                    )
                else:
                    # 使用简单重排序作为后备
                    simple_rerank = get_simple_rerank_service()
                    reranked_results = await simple_rerank.rerank(
                        query=query,
                        documents=merged_results,
                        top_k=min(100, len(merged_results))
                    )
            except Exception as e:
                logger.warning(f"Rerank failed: {e}, using merged results")
                reranked_results = merged_results
        else:
            reranked_results = []

        # 5. 分页返回
        total = len(reranked_results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = reranked_results[start_idx:end_idx]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }

    def _build_filter_conditions(
        self,
        tenant_id: str,
        category_id: Optional[str] = None,
        case_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> dict:
        """构建过滤条件"""
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
        return filter_conditions

    async def _keyword_search_all(
        self,
        query: str,
        filters: dict,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """关键词搜索（返回所有匹配结果，不分页）"""
        # 构建搜索查询
        if query and query.strip():
            search_query = {
                **filters,
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            }
        else:
            search_query = filters

        cursor = self.collection.find(search_query).limit(limit).sort("created_at", -1)

        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            doc["source"] = "keyword"
            items.append(doc)

        return items

    def _merge_results(
        self,
        keyword_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并关键词和向量搜索结果（去重）"""
        # 使用 case_id 作为唯一标识
        seen_ids = set()
        merged = []

        # 优先添加向量搜索结果（通常更相关）
        for item in vector_results:
            case_id = item.get("case_id") or item.get("id")
            if case_id and case_id not in seen_ids:
                seen_ids.add(case_id)
                merged.append(item)

        # 添加关键词搜索结果中的唯一项
        for item in keyword_results:
            case_id = item.get("id") or item.get("case_id")
            if case_id and case_id not in seen_ids:
                seen_ids.add(case_id)
                merged.append(item)

        return merged

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

    async def vector_only_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 20,
        case_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        仅使用向量搜索（用于 GraphRAG 场景）
        """
        if not self.milvus_service:
            return []

        try:
            query_vector = await self.embedding_service.embed_query(query)
            results = await self.milvus_service.search_similar(
                query_vector=query_vector,
                tenant_id=tenant_id,
                top_k=top_k,
                case_type=case_type
            )
            return results
        except Exception as e:
            logger.error(f"Vector only search failed: {e}")
            return []

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.database import CaseStatus
from app.tools.embedding import EmbeddingService
from app.services.milvus_service import get_milvus_service, MilvusService
from app.services.rerank_service import get_rerank_service, get_simple_rerank_service
from app.services.es_service import get_es_service, ElasticsearchService
from app.services.neo4j_service import get_neo4j_service, Neo4jService
import logging
import asyncio

logger = logging.getLogger(__name__)


class SearchService:
    """多路检索服务 - 结合 ES、向量、图谱搜索和 Rerank"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["cases"]
        self._milvus_service: Optional[MilvusService] = None
        self._es_service: Optional[ElasticsearchService] = None
        self._neo4j_service: Optional[Neo4jService] = None
        self._rerank_enabled = settings.RERANK_ENABLED

    @property
    def milvus_service(self) -> Optional[MilvusService]:
        """延迟获取 Milvus 服务"""
        if self._milvus_service is None:
            try:
                self._milvus_service = get_milvus_service()
            except Exception as e:
                logger.warning(f"Failed to get Milvus service: {e}")
        return self._milvus_service

    @property
    def es_service(self) -> Optional[ElasticsearchService]:
        """延迟获取 ES 服务"""
        if self._es_service is None:
            try:
                self._es_service = get_es_service()
            except Exception as e:
                logger.warning(f"Failed to get ES service: {e}")
        return self._es_service

    @property
    def neo4j_service(self) -> Optional[Neo4jService]:
        """延迟获取 Neo4j 服务"""
        if self._neo4j_service is None:
            try:
                self._neo4j_service = get_neo4j_service()
            except Exception as e:
                logger.warning(f"Failed to get Neo4j service: {e}")
        return self._neo4j_service

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
        多路检索案例
        结合 ES 全文检索、向量检索、图谱检索，并使用 Rerank 重排序
        """
        # 并行执行多路检索
        es_results, vector_results, graph_results = await self._parallel_search(
            query=query,
            tenant_id=tenant_id,
            category_id=category_id,
            case_type=case_type,
            tags=tags
        )

        # 合并结果（去重）
        merged_results = self._merge_results(es_results, vector_results, graph_results)

        # 5. 如果所有检索都失败，回退到 MongoDB 关键词搜索
        if not merged_results:
            filter_conditions = self._build_filter_conditions(
                tenant_id, category_id, case_type, tags
            )
            merged_results = await self._keyword_search_all(
                query, filter_conditions, limit=50
            )

        # 6. Rerank 重排序
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

        # 7. 分页返回
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
        """MongoDB 关键词搜索（回退方案）"""
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
            doc["source"] = "mongodb"
            items.append(doc)

        return items

    async def _parallel_search(
        self,
        query: str,
        tenant_id: str,
        category_id: Optional[str] = None,
        case_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> tuple:
        """
        并行执行多路检索（ES、向量、图谱）
        返回: (es_results, vector_results, graph_results)
        """
        # 创建搜索任务
        es_task = self._es_search(
            query=query,
            tenant_id=tenant_id,
            case_type=case_type,
            category_id=category_id,
            tags=tags
        ) if self.es_service and settings.ES_ENABLED else None

        vector_task = self._vector_search(
            query=query,
            tenant_id=tenant_id,
            case_type=case_type,
            category_id=category_id
        ) if self.milvus_service and query else None

        graph_task = self._graph_search(
            query=query,
            tenant_id=tenant_id,
            tags=tags
        ) if self.neo4j_service and settings.NEO4J_ENABLED else None

        # 并行执行所有搜索任务
        results = await asyncio.gather(
            es_task or [], vector_task or [], graph_task or [],
            return_exceptions=True
        )

        # 处理结果
        es_results = results[0] if not isinstance(results[0], Exception) else []
        vector_results = results[1] if not isinstance(results[1], Exception) else []
        graph_results = results[2] if not isinstance(results[2], Exception) else []

        return es_results, vector_results, graph_results

    async def _es_search(
        self,
        query: str,
        tenant_id: str,
        case_type: Optional[str] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Elasticsearch 全文检索"""
        try:
            return await self.es_service.search(
                query=query,
                tenant_id=tenant_id,
                top_k=50,
                case_type=case_type,
                category_id=category_id,
                tags=tags
            )
        except Exception as e:
            logger.warning(f"ES search failed: {e}")
            return []

    async def _vector_search(
        self,
        query: str,
        tenant_id: str,
        case_type: Optional[str] = None,
        category_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Milvus 向量搜索"""
        try:
            query_vector = await self.embedding_service.embed_query(query)
            return await self.milvus_service.search_similar(
                query_vector=query_vector,
                tenant_id=tenant_id,
                top_k=50,
                case_type=case_type,
                category_id=category_id
            )
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return []

    async def _graph_search(
        self,
        query: str,
        tenant_id: str,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Neo4j 图谱检索"""
        try:
            if tags:
                return await self.neo4j_service.search_by_tags(
                    tags=tags,
                    tenant_id=tenant_id,
                    top_k=30
                )
            elif query:
                return await self.neo4j_service.extract_keywords_and_search(
                    query=query,
                    tenant_id=tenant_id,
                    top_k=30
                )
            return []
        except Exception as e:
            logger.warning(f"Graph search failed: {e}")
            return []

    def _merge_results(
        self,
        es_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并多路检索结果（去重并计算综合分数）"""
        seen_ids = set()
        merged = []
        doc_scores = {}

        # 收集所有文档和分数
        for item in es_results:
            case_id = item.get("case_id") or item.get("id")
            if case_id:
                doc_scores[case_id] = doc_scores.get(case_id, {})
                doc_scores[case_id]["es"] = item.get("score", 1.0)
                if case_id not in seen_ids:
                    seen_ids.add(case_id)
                    merged.append(item)

        for item in vector_results:
            case_id = item.get("case_id") or item.get("id")
            if case_id:
                doc_scores[case_id] = doc_scores.get(case_id, {})
                doc_scores[case_id]["vector"] = item.get("score", 1.0)
                if case_id not in seen_ids:
                    seen_ids.add(case_id)
                    merged.append(item)

        for item in graph_results:
            case_id = item.get("case_id") or item.get("id")
            if case_id:
                doc_scores[case_id] = doc_scores.get(case_id, {})
                doc_scores[case_id]["graph"] = item.get("score", 1.0)
                if case_id not in seen_ids:
                    seen_ids.add(case_id)
                    merged.append(item)

        # 计算综合分数（加权平均）
        for item in merged:
            case_id = item.get("case_id") or item.get("id")
            if case_id and case_id in doc_scores:
                scores = doc_scores[case_id]
                # 综合分数 = 0.4 * ES + 0.4 * Vector + 0.2 * Graph
                combined_score = 0.0
                if "es" in scores:
                    combined_score += 0.4 * scores["es"]
                if "vector" in scores:
                    combined_score += 0.4 * scores["vector"]
                if "graph" in scores:
                    combined_score += 0.2 * scores["graph"]
                item["combined_score"] = combined_score

        # 按综合分数排序
        merged.sort(key=lambda x: x.get("combined_score", 0), reverse=True)

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

    async def get_related_cases(
        self,
        case_id: str,
        tenant_id: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取相关案例（基于图谱关系）
        """
        if not self.neo4j_service:
            return []

        try:
            return await self.neo4j_service.search_related_cases(
                case_id=case_id,
                tenant_id=tenant_id,
                top_k=top_k
            )
        except Exception as e:
            logger.error(f"Get related cases failed: {e}")
            return []

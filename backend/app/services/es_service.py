from typing import List, Optional, Dict, Any
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Elasticsearch 全文检索服务"""

    def __init__(self):
        self.host = settings.ES_HOST
        self.port = settings.ES_PORT
        self.index_name = settings.ES_INDEX
        self.enabled = settings.ES_ENABLED
        self._client: Optional[AsyncElasticsearch] = None

    async def get_client(self) -> Optional[AsyncElasticsearch]:
        """获取 ES 客户端"""
        if not self.enabled:
            logger.info("Elasticsearch is disabled")
            return None

        if self._client is None:
            try:
                self._client = AsyncElasticsearch(
                    hosts=[f"http://{self.host}:{self.port}"],
                    timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                # 测试连接
                await self._client.ping()
                logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}")
                self._client = None

        return self._client

    async def close(self):
        """关闭 ES 连接"""
        if self._client:
            await self._client.close()
            self._client = None

    async def create_index(self) -> bool:
        """创建案例索引"""
        client = await self.get_client()
        if client is None:
            return False

        try:
            # 检查索引是否已存在
            if await client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True

            # 定义索引映射
            mapping = {
                "mappings": {
                    "properties": {
                        "case_id": {"type": "keyword"},
                        "tenant_id": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "case_type": {"type": "keyword"},
                        "category_id": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }

            await client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    async def index_case(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        case_type: str = "external",
        category_id: str = "",
        tags: List[str] = None,
        status: str = "published"
    ) -> bool:
        """索引案例文档"""
        client = await self.get_client()
        if client is None:
            return False

        try:
            doc = {
                "case_id": case_id,
                "tenant_id": tenant_id,
                "title": title,
                "content": content,
                "case_type": case_type,
                "category_id": category_id or "",
                "tags": tags or [],
                "status": status
            }

            await client.index(index=self.index_name, id=case_id, document=doc)
            logger.info(f"Indexed case {case_id} in Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Failed to index case {case_id}: {e}")
            return False

    async def update_case(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        case_type: str = "external",
        category_id: str = "",
        tags: List[str] = None,
        status: str = "published"
    ) -> bool:
        """更新案例文档"""
        return await self.index_case(
            case_id=case_id,
            tenant_id=tenant_id,
            title=title,
            content=content,
            case_type=case_type,
            category_id=category_id,
            tags=tags,
            status=status
        )

    async def delete_case(self, case_id: str) -> bool:
        """删除案例文档"""
        client = await self.get_client()
        if client is None:
            return False

        try:
            await client.delete(index=self.index_name, id=case_id)
            logger.info(f"Deleted case {case_id} from Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Failed to delete case {case_id}: {e}")
            return False

    async def search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 50,
        case_type: Optional[str] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """全文搜索"""
        client = await self.get_client()
        if client is None:
            return []

        try:
            # 构建查询
            must_conditions = [
                {"term": {"tenant_id": tenant_id}},
                {"term": {"status": "published"}}
            ]

            if case_type:
                must_conditions.append({"term": {"case_type": case_type}})
            if category_id:
                must_conditions.append({"term": {"category_id": category_id}})
            if tags:
                must_conditions.append({"terms": {"tags": tags}})

            # 构建搜索体
            search_body = {
                "query": {
                    "bool": {
                        "must": must_conditions,
                        "should": [
                            {
                                "match": {
                                    "title": {
                                        "query": query,
                                        "boost": 2.0
                                    }
                                }
                            },
                            {
                                "match": {
                                    "content": {
                                        "query": query,
                                        "boost": 1.0
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1 if query else 0
                    }
                },
                "size": top_k,
                "_source": ["case_id", "tenant_id", "title", "content", "case_type", "category_id", "tags"]
            }

            response = await client.search(index=self.index_name, body=search_body)

            # 解析结果
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["score"] = hit["_score"]
                source["source"] = "elasticsearch"
                results.append(source)

            logger.info(f"Elasticsearch found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            return []

    async def batch_index_cases(self, cases: List[Dict[str, Any]]) -> int:
        """批量索引案例"""
        client = await self.get_client()
        if client is None:
            return 0

        try:
            actions = []
            for case in cases:
                actions.append({
                    "_index": self.index_name,
                    "_id": case["case_id"],
                    "_source": {
                        "case_id": case["case_id"],
                        "tenant_id": case["tenant_id"],
                        "title": case.get("title", ""),
                        "content": case.get("content", ""),
                        "case_type": case.get("case_type", "external"),
                        "category_id": case.get("category_id", ""),
                        "tags": case.get("tags", []),
                        "status": case.get("status", "published")
                    }
                })

            success, failed = await async_bulk(client, actions)
            logger.info(f"Batch indexed {success} cases, {failed} failed")
            return success
        except Exception as e:
            logger.error(f"Batch index failed: {e}")
            return 0


# 全局单例
_es_service: Optional[ElasticsearchService] = None


def get_es_service() -> ElasticsearchService:
    """获取 ES 服务单例"""
    global _es_service
    if _es_service is None:
        _es_service = ElasticsearchService()
    return _es_service

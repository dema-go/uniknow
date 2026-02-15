from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import asyncio

from app.core.config import settings
from app.models.database import Case, CaseStatus
from app.tools.embedding import EmbeddingService

logger = logging.getLogger(__name__)


class CaseService:
    """案例服务 - 集成多数据源同步（Milvus、ES、Neo4j）"""

    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["cases"]
        self.embedding_service = EmbeddingService()
        self._milvus_service = None
        self._es_service = None
        self._neo4j_service = None

    @property
    def milvus_service(self):
        """延迟获取 Milvus 服务"""
        if self._milvus_service is None:
            try:
                from app.services.milvus_service import get_milvus_service
                self._milvus_service = get_milvus_service()
            except Exception as e:
                logger.warning(f"Failed to get Milvus service: {e}")
        return self._milvus_service

    @property
    def es_service(self):
        """延迟获取 ES 服务"""
        if self._es_service is None:
            try:
                from app.services.es_service import get_es_service
                self._es_service = get_es_service()
            except Exception as e:
                logger.warning(f"Failed to get ES service: {e}")
        return self._es_service

    @property
    def neo4j_service(self):
        """延迟获取 Neo4j 服务"""
        if self._neo4j_service is None:
            try:
                from app.services.neo4j_service import get_neo4j_service
                self._neo4j_service = get_neo4j_service()
            except Exception as e:
                logger.warning(f"Failed to get Neo4j service: {e}")
        return self._neo4j_service

    async def _sync_to_all_sources(self, case: Case, case_id: str):
        """同步案例到所有数据源"""
        tasks = []

        # 同步到 Milvus
        if self.milvus_service:
            tasks.append(self._sync_to_milvus(case, case_id))

        # 同步到 ES
        if self.es_service and settings.ES_ENABLED:
            tasks.append(self._sync_to_es(case, case_id))

        # 同步到 Neo4j
        if self.neo4j_service and settings.NEO4J_ENABLED:
            tasks.append(self._sync_to_neo4j(case, case_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _sync_to_milvus(self, case: Case, case_id: str):
        """同步案例到 Milvus 向量数据库"""
        if not self.milvus_service:
            return

        try:
            # 生成向量
            text = f"{case.title}\n{case.content}"
            embedding = await self.embedding_service.embed_query(text)

            # 存储到 Milvus
            await self.milvus_service.insert_case(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                embedding=embedding,
                case_type=case.case_type or "external",
                category_id=case.category_id or ""
            )
            logger.info(f"Synced case {case_id} to Milvus")
        except Exception as e:
            logger.error(f"Failed to sync case {case_id} to Milvus: {e}")

    async def _sync_to_es(self, case: Case, case_id: str):
        """同步案例到 Elasticsearch"""
        if not self.es_service:
            return

        try:
            await self.es_service.index_case(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                case_type=case.case_type or "external",
                category_id=case.category_id or "",
                tags=case.tags or [],
                status=case.status
            )
            logger.info(f"Synced case {case_id} to Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to sync case {case_id} to Elasticsearch: {e}")

    async def _sync_to_neo4j(self, case: Case, case_id: str):
        """同步案例到 Neo4j 图数据库"""
        if not self.neo4j_service:
            return

        try:
            await self.neo4j_service.create_case_node(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                case_type=case.case_type or "external",
                category_id=case.category_id or "",
                tags=case.tags or []
            )
            logger.info(f"Synced case {case_id} to Neo4j")
        except Exception as e:
            logger.error(f"Failed to sync case {case_id} to Neo4j: {e}")

    async def _update_in_all_sources(self, case: Case, case_id: str):
        """更新所有数据源中的案例"""
        tasks = []

        # 更新 Milvus
        if self.milvus_service:
            tasks.append(self._update_in_milvus(case, case_id))

        # 更新 ES
        if self.es_service and settings.ES_ENABLED:
            tasks.append(self._update_in_es(case, case_id))

        # 更新 Neo4j
        if self.neo4j_service and settings.NEO4J_ENABLED:
            tasks.append(self._update_in_neo4j(case, case_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_in_milvus(self, case: Case, case_id: str):
        """更新 Milvus 中的案例向量"""
        if not self.milvus_service:
            return

        try:
            # 生成新向量
            text = f"{case.title}\n{case.content}"
            embedding = await self.embedding_service.embed_query(text)

            # 更新 Milvus
            await self.milvus_service.update_case(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                embedding=embedding,
                case_type=case.case_type or "external",
                category_id=case.category_id or ""
            )
            logger.info(f"Updated case {case_id} in Milvus")
        except Exception as e:
            logger.error(f"Failed to update case {case_id} in Milvus: {e}")

    async def _update_in_es(self, case: Case, case_id: str):
        """更新 Elasticsearch 中的案例"""
        if not self.es_service:
            return

        try:
            await self.es_service.update_case(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                case_type=case.case_type or "external",
                category_id=case.category_id or "",
                tags=case.tags or [],
                status=case.status
            )
            logger.info(f"Updated case {case_id} in Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to update case {case_id} in Elasticsearch: {e}")

    async def _update_in_neo4j(self, case: Case, case_id: str):
        """更新 Neo4j 中的案例节点"""
        if not self.neo4j_service:
            return

        try:
            await self.neo4j_service.update_case_node(
                case_id=case_id,
                tenant_id=case.tenant_id,
                title=case.title,
                content=case.content,
                case_type=case.case_type or "external",
                category_id=case.category_id or "",
                tags=case.tags or []
            )
            logger.info(f"Updated case {case_id} in Neo4j")
        except Exception as e:
            logger.error(f"Failed to update case {case_id} in Neo4j: {e}")

    async def _delete_from_all_sources(self, case_id: str):
        """从所有数据源删除案例"""
        tasks = []

        # 从 Milvus 删除
        if self.milvus_service:
            tasks.append(self._delete_from_milvus(case_id))

        # 从 ES 删除
        if self.es_service and settings.ES_ENABLED:
            tasks.append(self._delete_from_es(case_id))

        # 从 Neo4j 删除
        if self.neo4j_service and settings.NEO4J_ENABLED:
            tasks.append(self._delete_from_neo4j(case_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _delete_from_milvus(self, case_id: str):
        """从 Milvus 删除案例向量"""
        if not self.milvus_service:
            return

        try:
            await self.milvus_service.delete_case(case_id)
            logger.info(f"Deleted case {case_id} from Milvus")
        except Exception as e:
            logger.error(f"Failed to delete case {case_id} from Milvus: {e}")

    async def _delete_from_es(self, case_id: str):
        """从 Elasticsearch 删除案例"""
        if not self.es_service:
            return

        try:
            await self.es_service.delete_case(case_id)
            logger.info(f"Deleted case {case_id} from Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to delete case {case_id} from Elasticsearch: {e}")

    async def _delete_from_neo4j(self, case_id: str):
        """从 Neo4j 删除案例节点"""
        if not self.neo4j_service:
            return

        try:
            await self.neo4j_service.delete_case_node(case_id)
            logger.info(f"Deleted case {case_id} from Neo4j")
        except Exception as e:
            logger.error(f"Failed to delete case {case_id} from Neo4j: {e}")

    async def create_case(self, case_data: dict) -> Case:
        """创建案例"""
        # 设置默认值（如果case_data中没有提供）
        if "status" not in case_data:
            case_data["status"] = CaseStatus.DRAFT
        if "view_count" not in case_data:
            case_data["view_count"] = 0
        if "like_count" not in case_data:
            case_data["like_count"] = 0
        if "dislike_count" not in case_data:
            case_data["dislike_count"] = 0
        if "created_at" not in case_data:
            case_data["created_at"] = datetime.now()
        if "updated_at" not in case_data:
            case_data["updated_at"] = datetime.now()

        case = Case(**case_data)
        result = await self.collection.insert_one(case.model_dump(by_alias=True))
        case.id = str(result.inserted_id)

        # 同步到所有数据源（仅当案例已发布时）
        if case.status == CaseStatus.PUBLISHED:
            await self._sync_to_all_sources(case, case.id)

        return case

    async def get_case(self, case_id: str) -> Optional[Case]:
        """获取案例详情"""
        case = await self.collection.find_one({"_id": ObjectId(case_id)})
        if case:
            case["id"] = str(case.pop("_id"))
            return Case(**case)
        return None

    async def update_case(self, case_id: str, update_data: dict) -> Optional[Case]:
        """更新案例"""
        update_data["updated_at"] = datetime.now()
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(case_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = str(result.pop("_id"))
            case = Case(**result)

            # 同步到所有数据源（仅当案例已发布时）
            if case.status == CaseStatus.PUBLISHED:
                await self._update_in_all_sources(case, case_id)

            return case
        return None

    async def delete_case(self, case_id: str) -> bool:
        """删除案例"""
        result = await self.collection.delete_one({"_id": ObjectId(case_id)})

        if result.deleted_count > 0:
            # 从所有数据源删除
            await self._delete_from_all_sources(case_id)
            return True
        return False

    async def publish_case(self, case_id: str) -> Optional[Case]:
        """发布案例（状态变更为 published）"""
        case = await self.update_case(case_id, {"status": CaseStatus.PUBLISHED})
        if case:
            # 发布时同步到所有数据源
            await self._sync_to_all_sources(case, case_id)
        return case

    async def unpublish_case(self, case_id: str) -> Optional[Case]:
        """取消发布案例"""
        case = await self.update_case(case_id, {"status": CaseStatus.DRAFT})
        if case:
            # 从所有数据源删除
            await self._delete_from_all_sources(case_id)
        return case

    async def list_cases(
        self,
        tenant_id: str,
        keyword: Optional[str] = None,
        category_id: Optional[str] = None,
        case_type: Optional[str] = None,
        status: Optional[CaseStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """查询案例列表"""
        query = {"tenant_id": tenant_id}
        if keyword and keyword.strip():
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"content": {"$regex": keyword, "$options": "i"}},
            ]
        if category_id:
            query["category_id"] = category_id
        if case_type:
            query["case_type"] = case_type
        if status:
            query["status"] = status

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)

        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(Case(**doc))

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def increment_view(self, case_id: str):
        """增加浏览量"""
        await self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$inc": {"view_count": 1}}
        )

    async def get_statistics(self, tenant_id: str) -> dict:
        """获取案例统计"""
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": None,
                "total_cases": {"$sum": 1},
                "internal_cases": {
                    "$sum": {"$cond": [{"$eq": ["$case_type", "internal"]}, 1, 0]}
                },
                "external_cases": {
                    "$sum": {"$cond": [{"$eq": ["$case_type", "external"]}, 1, 0]}
                },
                "pending_approval": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending_approval"]}, 1, 0]}
                },
                "total_views": {"$sum": "$view_count"},
                "total_likes": {"$sum": "$like_count"},
                "total_dislikes": {"$sum": "$dislike_count"}
            }}
        ]
        result = await self.collection.aggregate(pipeline).to_list(None)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats
        return {
            "total_cases": 0,
            "internal_cases": 0,
            "external_cases": 0,
            "pending_approval": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_dislikes": 0
        }

    async def get_all_published_cases(self, tenant_id: str) -> List[dict]:
        """获取所有已发布的案例（用于数据迁移）"""
        cursor = self.collection.find({
            "tenant_id": tenant_id,
            "status": CaseStatus.PUBLISHED
        })

        cases = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            cases.append(doc)
        return cases

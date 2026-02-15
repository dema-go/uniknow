from typing import List, Optional, Dict, Any
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)
from app.core.config import settings
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def async_wrapper(func):
    """将同步函数包装为异步函数"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class MilvusService:
    """Milvus 向量数据库服务"""

    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.dimension = settings.EMBEDDING_DIMENSION
        self._collection: Optional[Collection] = None
        self._connected = False

    def connect(self) -> bool:
        """连接到 Milvus 服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """断开 Milvus 连接"""
        try:
            connections.disconnect("default")
            self._connected = False
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Failed to disconnect from Milvus: {e}")

    def create_collection(self) -> bool:
        """创建案例向量集合"""
        try:
            # 检查集合是否已存在
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection {self.collection_name} already exists")
                self._collection = Collection(self.collection_name)
                return True

            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True, auto_id=False),
                FieldSchema(name="case_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="tenant_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8000),
                FieldSchema(name="case_type", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="category_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            ]

            # 创建集合
            schema = CollectionSchema(fields=fields, description="案例向量集合")
            self._collection = Collection(name=self.collection_name, schema=schema)

            # 创建向量索引 (IVF_FLAT)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self._collection.create_index(field_name="embedding", index_params=index_params)

            logger.info(f"Created collection {self.collection_name} with index")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def get_collection(self) -> Optional[Collection]:
        """获取集合实例"""
        if not self._connected:
            self.connect()

        if self._collection is None:
            if utility.has_collection(self.collection_name):
                self._collection = Collection(self.collection_name)
            else:
                self.create_collection()

        return self._collection

    async def insert_case(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        embedding: List[float],
        case_type: str = "external",
        category_id: str = ""
    ) -> bool:
        """插入案例向量"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # 准备数据
            data = [
                [case_id],  # id (使用 case_id 作为主键)
                [case_id],  # case_id
                [tenant_id],
                [title[:500] if title else ""],  # 截断标题
                [content[:8000] if content else ""],  # 截断内容
                [case_type],
                [category_id or ""],
                [embedding],
            ]

            # 插入数据
            def _insert():
                collection.insert(data)
                collection.flush()

            await async_wrapper(_insert)()
            logger.info(f"Inserted case {case_id} into Milvus")
            return True
        except Exception as e:
            logger.error(f"Failed to insert case {case_id}: {e}")
            return False

    async def update_case(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        embedding: List[float],
        case_type: str = "external",
        category_id: str = ""
    ) -> bool:
        """更新案例向量（先删除后插入）"""
        try:
            # 先删除旧数据
            await self.delete_case(case_id)
            # 再插入新数据
            return await self.insert_case(
                case_id=case_id,
                tenant_id=tenant_id,
                title=title,
                content=content,
                embedding=embedding,
                case_type=case_type,
                category_id=category_id
            )
        except Exception as e:
            logger.error(f"Failed to update case {case_id}: {e}")
            return False

    async def delete_case(self, case_id: str) -> bool:
        """删除案例向量"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            def _delete():
                expr = f'id == "{case_id}"'
                collection.delete(expr)
                collection.flush()

            await async_wrapper(_delete)()
            logger.info(f"Deleted case {case_id} from Milvus")
            return True
        except Exception as e:
            logger.error(f"Failed to delete case {case_id}: {e}")
            return False

    async def search_similar(
        self,
        query_vector: List[float],
        tenant_id: str,
        top_k: int = 50,
        case_type: Optional[str] = None,
        category_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """向量相似度搜索"""
        try:
            collection = self.get_collection()
            if collection is None:
                return []

            # 加载集合到内存
            def _load():
                collection.load()

            await async_wrapper(_load)()

            # 构建过滤表达式
            filter_expr = f'tenant_id == "{tenant_id}"'
            if case_type:
                filter_expr += f' && case_type == "{case_type}"'
            if category_id:
                filter_expr += f' && category_id == "{category_id}"'

            # 搜索参数
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 16}
            }

            # 执行搜索
            def _search():
                results = collection.search(
                    data=[query_vector],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    expr=filter_expr,
                    output_fields=["case_id", "tenant_id", "title", "content", "case_type", "category_id"]
                )
                return results

            results = await async_wrapper(_search)()

            # 解析结果
            parsed_results = []
            for hits in results:
                for hit in hits:
                    parsed_results.append({
                        "case_id": hit.entity.get("case_id"),
                        "tenant_id": hit.entity.get("tenant_id"),
                        "title": hit.entity.get("title"),
                        "content": hit.entity.get("content"),
                        "case_type": hit.entity.get("case_type"),
                        "category_id": hit.entity.get("category_id"),
                        "score": float(hit.score),  # 相似度分数
                        "source": "vector"
                    })

            logger.info(f"Found {len(parsed_results)} similar cases")
            return parsed_results
        except Exception as e:
            logger.error(f"Failed to search similar cases: {e}")
            return []

    async def batch_insert_cases(self, cases: List[Dict[str, Any]]) -> int:
        """批量插入案例向量"""
        success_count = 0
        for case in cases:
            if await self.insert_case(**case):
                success_count += 1
        return success_count


# 全局单例
_milvus_service: Optional[MilvusService] = None


def get_milvus_service() -> MilvusService:
    """获取 Milvus 服务单例"""
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
        _milvus_service.connect()
        _milvus_service.create_collection()
    return _milvus_service

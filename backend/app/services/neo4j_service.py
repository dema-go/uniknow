from typing import List, Optional, Dict, Any
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Neo4j 图数据库服务 - 用于知识图谱检索"""

    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.enabled = settings.NEO4J_ENABLED
        self._driver: Optional[AsyncDriver] = None

    async def get_driver(self) -> Optional[AsyncDriver]:
        """获取 Neo4j 驱动"""
        if not self.enabled:
            logger.info("Neo4j is disabled")
            return None

        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                # 测试连接
                await self._driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {self.uri}")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                self._driver = None

        return self._driver

    async def close(self):
        """关闭 Neo4j 连接"""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def create_constraints(self) -> bool:
        """创建约束和索引"""
        driver = await self.get_driver()
        if driver is None:
            return False

        try:
            async with driver.session() as session:
                # 创建案例节点唯一约束
                await session.run(
                    "CREATE CONSTRAINT case_id_unique IF NOT EXISTS "
                    "FOR (c:Case) REQUIRE c.case_id IS UNIQUE"
                )
                # 创建租户索引
                await session.run(
                    "CREATE INDEX case_tenant_idx IF NOT EXISTS "
                    "FOR (c:Case) ON (c.tenant_id)"
                )
                # 创建标签索引
                await session.run(
                    "CREATE INDEX tag_name_idx IF NOT EXISTS "
                    "FOR (t:Tag) ON (t.name)"
                )
                # 创建分类索引
                await session.run(
                    "CREATE INDEX category_name_idx IF NOT EXISTS "
                    "FOR (cat:Category) ON (cat.name)"
                )

            logger.info("Created Neo4j constraints and indexes")
            return True
        except Exception as e:
            logger.error(f"Failed to create constraints: {e}")
            return False

    async def create_case_node(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        case_type: str = "external",
        category_id: str = "",
        tags: List[str] = None
    ) -> bool:
        """创建案例节点及其关系"""
        driver = await self.get_driver()
        if driver is None:
            return False

        try:
            async with driver.session() as session:
                # 创建案例节点
                await session.run(
                    """
                    MERGE (c:Case {case_id: $case_id})
                    SET c.tenant_id = $tenant_id,
                        c.title = $title,
                        c.content = $content,
                        c.case_type = $case_type,
                        c.category_id = $category_id
                    """,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    title=title,
                    content=content,
                    case_type=case_type,
                    category_id=category_id or ""
                )

                # 创建分类节点并建立关系
                if category_id:
                    await session.run(
                        """
                        MATCH (c:Case {case_id: $case_id})
                        MERGE (cat:Category {id: $category_id})
                        MERGE (c)-[:BELONGS_TO]->(cat)
                        """,
                        case_id=case_id,
                        category_id=category_id
                    )

                # 创建标签节点并建立关系
                if tags:
                    for tag in tags:
                        await session.run(
                            """
                            MATCH (c:Case {case_id: $case_id})
                            MERGE (t:Tag {name: $tag})
                            MERGE (c)-[:HAS_TAG]->(t)
                            """,
                            case_id=case_id,
                            tag=tag
                        )

            logger.info(f"Created case node {case_id} in Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to create case node {case_id}: {e}")
            return False

    async def update_case_node(
        self,
        case_id: str,
        tenant_id: str,
        title: str,
        content: str,
        case_type: str = "external",
        category_id: str = "",
        tags: List[str] = None
    ) -> bool:
        """更新案例节点"""
        driver = await self.get_driver()
        if driver is None:
            return False

        try:
            # 先删除旧的关系，再重新创建
            async with driver.session() as session:
                await session.run(
                    """
                    MATCH (c:Case {case_id: $case_id})-[r]->()
                    DELETE r
                    """,
                    case_id=case_id
                )

            return await self.create_case_node(
                case_id=case_id,
                tenant_id=tenant_id,
                title=title,
                content=content,
                case_type=case_type,
                category_id=category_id,
                tags=tags
            )
        except Exception as e:
            logger.error(f"Failed to update case node {case_id}: {e}")
            return False

    async def delete_case_node(self, case_id: str) -> bool:
        """删除案例节点及其关系"""
        driver = await self.get_driver()
        if driver is None:
            return False

        try:
            async with driver.session() as session:
                await session.run(
                    """
                    MATCH (c:Case {case_id: $case_id})
                    DETACH DELETE c
                    """,
                    case_id=case_id
                )

            logger.info(f"Deleted case node {case_id} from Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to delete case node {case_id}: {e}")
            return False

    async def search_by_tags(
        self,
        tags: List[str],
        tenant_id: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """通过标签关系搜索相关案例"""
        driver = await self.get_driver()
        if driver is None:
            return []

        try:
            async with driver.session() as session:
                result = await session.run(
                    """
                    MATCH (c:Case)-[:HAS_TAG]->(t:Tag)
                    WHERE t.name IN $tags AND c.tenant_id = $tenant_id
                    WITH c, COUNT(t) AS tag_count
                    ORDER BY tag_count DESC
                    LIMIT $top_k
                    RETURN c.case_id AS case_id,
                           c.tenant_id AS tenant_id,
                           c.title AS title,
                           c.content AS content,
                           c.case_type AS case_type,
                           c.category_id AS category_id,
                           tag_count AS score
                    """,
                    tags=tags,
                    tenant_id=tenant_id,
                    top_k=top_k
                )

                records = await result.data()
                results = []
                for record in records:
                    record["source"] = "neo4j"
                    results.append(record)

                logger.info(f"Neo4j found {len(results)} cases by tags")
                return results
        except Exception as e:
            logger.error(f"Neo4j tag search failed: {e}")
            return []

    async def search_by_category(
        self,
        category_id: str,
        tenant_id: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """通过分类关系搜索案例"""
        driver = await self.get_driver()
        if driver is None:
            return []

        try:
            async with driver.session() as session:
                result = await session.run(
                    """
                    MATCH (c:Case)-[:BELONGS_TO]->(cat:Category {id: $category_id})
                    WHERE c.tenant_id = $tenant_id
                    RETURN c.case_id AS case_id,
                           c.tenant_id AS tenant_id,
                           c.title AS title,
                           c.content AS content,
                           c.case_type AS case_type,
                           c.category_id AS category_id
                    LIMIT $top_k
                    """,
                    category_id=category_id,
                    tenant_id=tenant_id,
                    top_k=top_k
                )

                records = await result.data()
                results = []
                for record in records:
                    record["source"] = "neo4j"
                    record["score"] = 1.0
                    results.append(record)

                return results
        except Exception as e:
            logger.error(f"Neo4j category search failed: {e}")
            return []

    async def search_related_cases(
        self,
        case_id: str,
        tenant_id: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索与指定案例相关的其他案例（通过共享标签或分类）"""
        driver = await self.get_driver()
        if driver is None:
            return []

        try:
            async with driver.session() as session:
                result = await session.run(
                    """
                    MATCH (c:Case {case_id: $case_id})-[:HAS_TAG|BELONGS_TO]->(n)
                    MATCH (related:Case)-[:HAS_TAG|BELONGS_TO]->(n)
                    WHERE related.case_id <> $case_id
                      AND related.tenant_id = $tenant_id
                    WITH related, COUNT(n) AS relation_strength
                    ORDER BY relation_strength DESC
                    LIMIT $top_k
                    RETURN related.case_id AS case_id,
                           related.tenant_id AS tenant_id,
                           related.title AS title,
                           related.content AS content,
                           related.case_type AS case_type,
                           related.category_id AS category_id,
                           relation_strength AS score
                    """,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    top_k=top_k
                )

                records = await result.data()
                results = []
                for record in records:
                    record["source"] = "neo4j"
                    results.append(record)

                return results
        except Exception as e:
            logger.error(f"Neo4j related search failed: {e}")
            return []

    async def extract_keywords_and_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """从查询中提取关键词并搜索相关案例"""
        # 简单的关键词提取（可以后续替换为 NLP 方法）
        keywords = query.split()
        return await self.search_by_tags(keywords, tenant_id, top_k)


# 全局单例
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """获取 Neo4j 服务单例"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service

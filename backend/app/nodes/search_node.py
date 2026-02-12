from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda

from app.graph.state import GraphState
from app.services.search_service import SearchService


async def retrieve_documents(state: GraphState) -> GraphState:
    """检索相关文档"""
    search_service = SearchService()

    # 检索与问题相关的文档
    results = await search_service.search_cases(
        query=state.question,
        tenant_id=state.tenant_id,
        page=5
    )

    return GraphState(
        **state.model_dump(),
        retrieved_docs=results.get("items", []),
        step="retrieve"
    )


async def extract_entities(state: GraphState) -> GraphState:
    """从问题中提取实体"""
    # TODO: 使用 LLM 从问题中提取实体
    entities = []

    # 简单示例：提取关键词
    keywords = state.question.split()
    for kw in keywords:
        if len(kw) > 2:
            entities.append({
                "name": kw,
                "type": "keyword",
                "confidence": 0.5
            })

    return GraphState(
        **state.model_dump(),
        graph_entities=entities,
        step="extract"
    )


async def retrieve_graph_context(state: GraphState) -> GraphState:
    """从知识图谱中检索上下文"""
    # TODO: 实现图谱检索逻辑
    # 从 Neo4j 或其他图数据库中检索相关实体和关系

    return GraphState(
        **state.model_dump(),
        entity_relations=[],
        step="graph_retrieve"
    )

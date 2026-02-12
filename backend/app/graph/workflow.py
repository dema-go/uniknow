from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.nodes.search_node import retrieve_documents, extract_entities, retrieve_graph_context
from app.nodes.rag_node import generate_answer, evaluate_answer, reformulate_query


def build_graph_rag_workflow() -> StateGraph:
    """
    构建 GraphRag 工作流

    工作流流程：
    start -> extract_entities -> reformulate_query -> retrieve_documents
         -> generate_answer -> evaluate_answer -> END
              |
              +-> (低置信度) -> reformulate_query
    """

    # 创建状态图
    workflow = StateGraph(GraphState)

    # 添加节点
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("reformulate_query", reformulate_query)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("evaluate_answer", evaluate_answer)

    # 设置入口
    workflow.set_entry_point("extract_entities")

    # 设置边
    workflow.add_edge("extract_entities", "reformulate_query")
    workflow.add_edge("reformulate_query", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "generate_answer")
    workflow.add_edge("generate_answer", "evaluate_answer")

    # 条件边：评估后根据置信度决定是否重新生成
    workflow.add_conditional_edges(
        "evaluate_answer",
        lambda x: "END" if x["confidence"] >= 0.7 else "reformulate_query",
        {
            "END": END,
            "reformulate_query": "reformulate_query"
        }
    )

    return workflow.compile()

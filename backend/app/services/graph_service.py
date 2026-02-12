from typing import Optional
from app.graph.workflow import build_graph_rag_workflow


class GraphService:
    """GraphRag 服务"""

    def __init__(self):
        self.workflow = build_graph_rag_workflow()

    async def ask_question(
        self,
        question: str,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> dict:
        """
        智能问答
        使用 GraphRag 进行问答
        """
        # 初始化图状态
        initial_state = {
            "question": question,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "retrieved_docs": [],
            "graph_entities": [],
            "answer": "",
            "sources": [],
            "confidence": 0.0
        }

        # 执行图工作流
        final_state = await self.workflow.ainvoke(initial_state)

        return {
            "answer": final_state.get("answer", ""),
            "sources": final_state.get("sources", []),
            "graph_context": final_state.get("graph_entities", []),
            "confidence": final_state.get("confidence", 0.0)
        }

from typing import AsyncGenerator, Optional
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
        智能问答（同步）
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

    async def ask_question_stream(
        self,
        question: str,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """
        智能问答（流式）
        使用 GraphRag 进行问答，返回异步生成器
        """
        # 发送思考状态
        yield {"type": "thinking", "message": "正在搜索相关案例..."}
        yield {"type": "thinking", "message": "正在提取实体关系..."}
        yield {"type": "thinking", "message": "正在生成答案..."}

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

        # 流式发送答案内容
        answer = final_state.get("answer", "")
        if answer:
            # 将答案分块发送，实现打字机效果
            chunk_size = 20  # 每次发送20个字符
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i + chunk_size]
                yield {"type": "content", "text": chunk}

        # 发送来源信息
        sources = final_state.get("sources", [])
        if sources:
            yield {"type": "source", "sources": sources}

        # 发送置信度
        confidence = final_state.get("confidence", 0.0)
        if confidence > 0:
            yield {"type": "confidence", "value": confidence}

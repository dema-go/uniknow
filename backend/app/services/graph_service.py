from typing import AsyncGenerator, Optional
import asyncio
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
        真正的流式输出：在处理过程中实时推送状态
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

        try:
            # 使用 astream 流式处理工作流
            current_state = initial_state

            async for event in self.workflow.astream(initial_state):
                # event 是一个字典，包含节点名称和该节点的输出
                for node_name, node_output in event.items():
                    # 更新当前状态
                    if isinstance(node_output, dict):
                        current_state.update(node_output)

                    # 根据节点类型发送不同的思考状态
                    if "extract" in node_name.lower() or "entity" in node_name.lower():
                        yield {"type": "thinking", "message": "正在提取关键信息..."}
                    elif "search" in node_name.lower() or "retrieve" in node_name.lower():
                        yield {"type": "thinking", "message": "正在搜索相关案例..."}
                    elif "reformulate" in node_name.lower():
                        yield {"type": "thinking", "message": "正在优化问题..."}
                    elif "generate" in node_name.lower():
                        yield {"type": "thinking", "message": "正在生成答案..."}

                        # 如果有答案，立即开始流式发送
                        answer = node_output.get("answer", "") if isinstance(node_output, dict) else ""
                        if answer:
                            # 分块发送，模拟打字效果
                            chunk_size = 15
                            for i in range(0, len(answer), chunk_size):
                                chunk = answer[i:i + chunk_size]
                                yield {"type": "content", "text": chunk}
                                # 添加小延迟，模拟打字效果
                                await asyncio.sleep(0.05)

                    elif "evaluate" in node_name.lower():
                        yield {"type": "thinking", "message": "正在评估答案质量..."}
                    elif "context" in node_name.lower():
                        yield {"type": "thinking", "message": "正在构建上下文..."}

            # 发送来源信息
            sources = current_state.get("sources", [])
            if sources:
                yield {"type": "source", "sources": sources}

            # 发送置信度
            confidence = current_state.get("confidence", 0.0)
            if confidence > 0:
                yield {"type": "confidence", "value": confidence}

        except Exception as e:
            # 如果流式处理失败，回退到同步处理
            yield {"type": "thinking", "message": "正在处理问题..."}
            final_state = await self.workflow.ainvoke(initial_state)

            # 流式发送答案内容
            answer = final_state.get("answer", "")
            if answer:
                chunk_size = 15
                for i in range(0, len(answer), chunk_size):
                    chunk = answer[i:i + chunk_size]
                    yield {"type": "content", "text": chunk}
                    await asyncio.sleep(0.05)

            # 发送来源信息
            sources = final_state.get("sources", [])
            if sources:
                yield {"type": "source", "sources": sources}

from typing import Dict, Any
from openai import OpenAI
from app.graph.state import GraphState
from app.core.config import settings


async def generate_answer(state: GraphState) -> GraphState:
    """生成最终答案"""
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )

    # 构造上下文
    docs_context = "\n\n".join([
        f"【文档{i+1}】{doc.get('content', '')}"
        for i, doc in enumerate(state.retrieved_docs[:3])
    ])

    graph_context = ""
    if state.graph_entities:
        entities = [e.get("name", "") for e in state.graph_entities]
        graph_context = f"\n相关实体: {', '.join(entities)}"

    # 构建提示词
    system_prompt = """你是一个智能客服助手，专注于回答用户关于产品和服务的问题。
请基于提供的文档和知识图谱信息，给出准确、专业的回答。

要求：
1. 回答要简洁明了，条理清晰
2. 如果文档中有相关内容，优先引用文档
3. 如果无法确定答案，请明确告知用户
4. 适当使用列表和编号提高可读性
"""

    user_prompt = f"""用户问题：{state.question}

参考文档：
{docs_context}
{graph_context}

请根据以上信息回答用户问题："""

    # 调用 LLM 生成回答
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    # 构建来源
    sources = [
        {
            "id": doc.get("id"),
            "title": doc.get("title"),
            "relevance": 0.9 - i * 0.1
        }
        for i, doc in enumerate(state.retrieved_docs[:3])
    ]

    return GraphState(
        **state.model_dump(),
        answer=answer,
        sources=sources,
        confidence=0.85,
        step="generate"
    )


async def evaluate_answer(state: GraphState) -> GraphState:
    """评估回答质量"""
    # TODO: 实现回答质量评估逻辑
    # 可以使用 LLM 评估回答的相关性、准确性、完整性

    return GraphState(
        **state.model_dump(),
        confidence=0.9,
        step="evaluate"
    )


async def reformulate_query(state: GraphState) -> GraphState:
    """重构查询"""
    # TODO: 使用 LLM 重构查询，使其更适合检索

    return GraphState(
        **state.model_dump(),
        reformulated_query=state.question,
        step="reformulate"
    )

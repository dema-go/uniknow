from typing import List, Optional, Dict, Any, TypedDict


class GraphState(TypedDict):
    """GraphRag 图状态 - LangGraph 状态定义"""

    # 输入
    question: str                      # 用户问题
    tenant_id: str                     # 租户ID
    user_id: Optional[str]              # 用户ID

    # 中间状态
    retrieved_docs: List[dict]          # 检索到的文档
    graph_entities: List[dict]            # 图谱实体
    entity_relations: List[dict]          # 实体关系
    reformulated_query: str               # 重构的查询

    # 输出
    answer: str                         # 生成的回答
    sources: List[dict]                 # 参考来源
    confidence: float                    # 置信度

    # 元数据
    step: str                           # 当前步骤
    error: Optional[str]                 # 错误信息

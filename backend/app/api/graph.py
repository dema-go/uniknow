import json
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.schemas.common import BaseResponse
from app.models.user import TokenData
from app.core.security import get_current_user
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["智能问答"])


class AskRequest(BaseModel):
    """问答请求模型"""
    question: str = Field(..., description="问题", min_length=1)
    session_id: Optional[str] = Field(None, description="会话ID")


async def stream_generator(question: str, tenant_id: str, user_id: str):
    """SSE流式响应生成器"""
    graph_service = GraphService()

    try:
        # 发送开始事件
        yield f"event: start\ndata: {json.dumps({'message': '开始处理问题'})}\n\n"

        # 发送思考状态
        yield f"event: thinking\ndata: {json.dumps({'message': '正在分析问题...'})}\n\n"

        # 获取答案
        result = await graph_service.ask_question_stream(
            question=question,
            tenant_id=tenant_id,
            user_id=user_id
        )

        # 流式发送答案内容
        async for chunk in result:
            if chunk.get("type") == "content":
                yield f"event: content\ndata: {json.dumps({'text': chunk.get('text', '')})}\n\n"
            elif chunk.get("type") == "source":
                yield f"event: sources\ndata: {json.dumps({'sources': chunk.get('sources', [])})}\n\n"
            elif chunk.get("type") == "thinking":
                yield f"event: thinking\ndata: {json.dumps({'message': chunk.get('message', '')})}\n\n"

        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({})}\n\n"

    except Exception as e:
        # 发送错误事件
        yield f"event: error\ndata: {json.dumps({'message': f'处理失败: {str(e)}'})}\n\n"


@router.post("/ask")
async def ask_question(
    request_data: AskRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """智能问答 - GraphRag SSE流式响应"""
    return StreamingResponse(
        stream_generator(
            question=request_data.question,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/ask-sync", response_model=BaseResponse)
async def ask_question_sync(
    request_data: AskRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """智能问答 - 同步响应（保留用于兼容）"""
    try:
        graph_service = GraphService()
        result = await graph_service.ask_question(
            question=request_data.question,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id
        )
        return BaseResponse(data=result)
    except Exception as e:
        return BaseResponse(code=500, message=f"问答失败: {str(e)}")

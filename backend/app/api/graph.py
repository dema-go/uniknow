from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.common import BaseResponse
from app.core.security import get_current_user
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["智能问答"])


class AskRequest(BaseModel):
    """问答请求模型"""
    question: str
    session_id: str = None


@router.post("/ask", response_model=BaseResponse)
async def ask_question(
    request_data: AskRequest,
    user_id: str = Depends(get_current_user)
):
    """智能问答 - GraphRag"""
    try:
        graph_service = GraphService()
        result = await graph_service.ask_question(
            question=request_data.question,
            tenant_id=user_id,
            user_id=user_id
        )
        return BaseResponse(data=result)
    except Exception as e:
        return BaseResponse(code=500, message=f"问答失败: {str(e)}")

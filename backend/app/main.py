from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import (
    case_router,
    search_router,
    approval_router,
    operation_router
)

app = FastAPI(
    title="UniKnow API",
    description="案例管理系统后端服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(case_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(approval_router, prefix="/api/v1")
app.include_router(operation_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "UniKnow API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )

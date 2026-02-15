"""
文件上传/下载 API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.schemas.common import BaseResponse
from app.models.user import TokenData
from app.core.security import get_current_user
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/files", tags=["文件管理"])


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_name: str
    file_path: str       # MinIO 对象名
    file_url: str        # 访问 URL
    file_size: int
    file_type: str


# 支持的文件类型
ALLOWED_EXTENSIONS = {
    # 文档
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    # 文本
    'txt', 'md',
    # 压缩包
    'zip', 'rar',
}

# 文件大小限制 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload", response_model=BaseResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    """
    上传文件到 MinIO

    支持的文件类型：
    - 文档：pdf, doc, docx, xls, xlsx, ppt, pptx
    - 文本：txt, md
    - 其他：zip, rar

    文件大小限制：50MB
    """
    # 检查文件扩展名
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: .{ext}。支持的类型: {', '.join('.' + e for e in ALLOWED_EXTENSIONS)}"
        )

    # 读取文件内容
    content = await file.read()

    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")

    # 上传到 MinIO
    storage = get_storage_service()
    object_name, file_url = storage.upload_file(
        file_content=content,
        file_name=file.filename,
        content_type=file.content_type or "application/octet-stream",
        tenant_id=current_user.tenant_id
    )

    return BaseResponse(
        data=FileUploadResponse(
            file_name=file.filename,
            file_path=object_name,
            file_url=file_url,
            file_size=len(content),
            file_type=file.content_type or "application/octet-stream"
        ).model_dump()
    )


@router.get("/{bucket}/{object_name:path}")
async def download_file(
    bucket: str,
    object_name: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    下载文件

    Args:
        bucket: bucket 名称
        object_name: 对象名称 (路径格式: tenant_id/uuid.ext)
    """
    storage = get_storage_service()

    try:
        content, content_type = storage.get_file(f"{bucket}/{object_name}")

        # 从 object_name 中提取文件名
        filename = object_name.split('/')[-1]

        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.delete("/{bucket}/{object_name:path}")
async def delete_file(
    bucket: str,
    object_name: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    删除文件

    Args:
        bucket: bucket 名称
        object_name: 对象名称
    """
    storage = get_storage_service()

    success = storage.delete_file(f"{bucket}/{object_name}")
    if not success:
        raise HTTPException(status_code=500, detail="删除文件失败")

    return BaseResponse(data={"success": True})

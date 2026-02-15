"""
MinIO 文件存储服务
"""
import io
import logging
import uuid
from typing import Tuple, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class MinIOStorageService:
    """MinIO 文件存储服务"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        try:
            from minio import Minio
            from minio.error import S3Error

            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_USE_SSL
            )
            self.bucket_name = settings.MINIO_BUCKET_NAME
            self._ensure_bucket()
            self._initialized = True
            logger.info(f"MinIO storage service initialized: {settings.MINIO_ENDPOINT}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.client = None
            self.bucket_name = None
            self._initialized = False

    def _ensure_bucket(self):
        """确保 bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")

    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        tenant_id: str
    ) -> Tuple[str, str]:
        """
        上传文件到 MinIO

        Args:
            file_content: 文件内容（字节）
            file_name: 原始文件名
            content_type: 文件 MIME 类型
            tenant_id: 租户 ID

        Returns:
            Tuple[object_name, file_url]
        """
        if not self.client:
            raise RuntimeError("MinIO client not initialized")

        # 生成唯一对象名：tenant_id/uuid.ext
        ext = file_name.rsplit('.', 1)[-1] if '.' in file_name else ''
        object_name = f"{tenant_id}/{uuid.uuid4().hex}.{ext}" if ext else f"{tenant_id}/{uuid.uuid4().hex}"

        # 上传文件
        self.client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(file_content),
            length=len(file_content),
            content_type=content_type
        )

        # 生成访问 URL
        file_url = self._get_file_url(object_name)
        return object_name, file_url

    def _get_file_url(self, object_name: str) -> str:
        """获取文件访问 URL"""
        protocol = "https" if settings.MINIO_USE_SSL else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"

    def get_file(self, object_name: str) -> Tuple[bytes, str]:
        """
        获取文件内容

        Args:
            object_name: 对象名称

        Returns:
            Tuple[content, content_type]
        """
        if not self.client:
            raise RuntimeError("MinIO client not initialized")

        response = self.client.get_object(self.bucket_name, object_name)
        content = response.read()
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        response.close()
        response.release_conn()
        return content, content_type

    def delete_file(self, object_name: str) -> bool:
        """
        删除文件

        Args:
            object_name: 对象名称

        Returns:
            是否删除成功
        """
        if not self.client:
            raise RuntimeError("MinIO client not initialized")

        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False


# 单例获取函数
def get_storage_service() -> MinIOStorageService:
    return MinIOStorageService()

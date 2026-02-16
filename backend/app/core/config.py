from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # 数据库配置
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "uniknow"
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI/DashScope 配置
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    OPENAI_MODEL: str = "qwen-plus"
    OPENAI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    EMBEDDING_MODEL: str = "text-embedding-v2"
    EMBEDDING_DIMENSION: int = 1024  # text-embedding-v2 向量维度

    # Milvus 向量数据库配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "cases"

    # Rerank 配置
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANK_DEVICE: str = "cpu"  # 或 "cuda" / "mps"
    RERANK_ENABLED: bool = True

    # 智谱 Rerank 配置（优先使用）
    ZHIPU_API_KEY: str = Field(default="", description="智谱AI API Key")
    ZHIPU_RERANK_MODEL: str = "glm-rerank"  # 可选: glm-rerank, glm-rerank-pro
    ZHIPU_RERANK_ENABLED: bool = True  # 是否启用智谱 Rerank

    # Elasticsearch 配置
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_INDEX: str = "cases"
    ES_ENABLED: bool = True

    # Neo4j 配置
    NEO4J_URI: str = "bolt://localhost:7688"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "uniknow123"
    NEO4J_ENABLED: bool = True

    # MinIO 文件存储配置
    MINIO_ENDPOINT: str = "localhost:9002"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "uniknow-documents"
    MINIO_USE_SSL: bool = False

    # JWT配置
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    model_config = SettingsConfigDict(
        env_file="/Users/liuziying/uniknow/backend/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

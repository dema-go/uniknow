from pydantic import Field
from pydantic_settings import BaseSettings


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
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

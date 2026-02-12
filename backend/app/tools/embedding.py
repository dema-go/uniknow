from typing import List
from openai import AsyncOpenAI
from app.core.config import settings


class EmbeddingService:
    """向量嵌入服务 - 适配阿里云 DashScope OpenAI兼容模式"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.EMBEDDING_MODEL

    async def embed_query(self, query: str) -> List[float]:
        """生成查询向量 - 阿里云 DashScope OpenAI兼容模式"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=query
        )
        return response.data[0].embedding

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """批量生成文档向量 - 阿里云 DashScope OpenAI兼容模式"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=documents
        )
        return [item.embedding for item in response.data]

    async def similarity_search(
        self,
        query_vector: List[float],
        vectors: List[List[float]],
        top_k: int = 5
    ) -> List[int]:
        """计算相似度并返回 top_k 索引"""
        import numpy as np

        query_np = np.array(query_vector)
        vectors_np = np.array(vectors)

        # 余弦相似度
        similarities = np.dot(vectors_np, query_np) / (
            np.linalg.norm(vectors_np, axis=1) * np.linalg.norm(query_np)
        )

        # 返回 top_k 索引
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return top_indices.tolist()

from typing import List, Dict, Any, Optional
import logging
import asyncio
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)


def async_wrapper(func):
    """将同步函数包装为异步函数"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class RerankService:
    """Rerank 重排序服务 - 使用 BGE-Reranker 模型"""

    def __init__(self):
        self.model_name = settings.RERANK_MODEL
        self.device = settings.RERANK_DEVICE
        self.enabled = settings.RERANK_ENABLED
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """延迟加载模型"""
        if self._model is not None:
            return

        if not self.enabled:
            logger.info("Rerank is disabled, skipping model loading")
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            logger.info(f"Loading rerank model: {self.model_name}")

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()

            logger.info(f"Rerank model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load rerank model: {e}")
            self.enabled = False

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        对文档进行重排序

        Args:
            query: 查询文本
            documents: 文档列表，每个文档必须包含 'title' 或 'content' 字段
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表，按相关性降序排列
        """
        if not self.enabled:
            logger.info("Rerank is disabled, returning original documents")
            return documents[:top_k]

        if not documents:
            return []

        try:
            # 确保模型已加载
            self._load_model()

            if self._model is None:
                logger.warning("Rerank model not loaded, returning original documents")
                return documents[:top_k]

            # 构造文档文本（用于 rerank）
            doc_texts = []
            for doc in documents:
                # 优先使用标题+内容的组合
                title = doc.get("title", "")
                content = doc.get("content", "")
                if title and content:
                    doc_texts.append(f"{title}\n{content[:500]}")  # 限制长度
                elif content:
                    doc_texts.append(content[:500])
                else:
                    doc_texts.append(title)

            # 计算 cross-encoder 分数
            scores = await self._compute_scores(query, doc_texts)

            # 按分数排序
            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # 返回 top_k 结果
            results = []
            for doc, score in scored_docs[:top_k]:
                result = doc.copy()
                result["rerank_score"] = float(score)
                results.append(result)

            logger.info(f"Reranked {len(documents)} documents, returning top {len(results)}")
            return results

        except Exception as e:
            logger.error(f"Failed to rerank documents: {e}")
            return documents[:top_k]

    async def _compute_scores(self, query: str, documents: List[str]) -> List[float]:
        """计算 cross-encoder 分数"""
        import torch

        def _compute():
            # 构造 [query, doc] 对
            pairs = [[query, doc] for doc in documents]

            # Tokenize
            inputs = self._tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 计算分数
            with torch.no_grad():
                scores = self._model(**inputs).logits.squeeze(-1)

            # 归一化到 0-1
            scores = torch.sigmoid(scores)

            return scores.cpu().tolist()

        return await async_wrapper(_compute)()


class SimpleRerankService:
    """简单的 Rerank 服务（不使用模型，基于规则）"""

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        基于规则的简单重排序
        主要考虑：标题匹配、内容匹配、关键词密度等
        """
        if not documents:
            return []

        query_terms = set(query.lower().split())

        def calculate_score(doc: Dict[str, Any]) -> float:
            score = 0.0
            title = doc.get("title", "").lower()
            content = doc.get("content", "").lower()

            # 标题完全匹配加分
            if query.lower() in title:
                score += 10.0

            # 标题中包含查询词
            title_terms = set(title.split())
            title_overlap = len(query_terms & title_terms)
            score += title_overlap * 2.0

            # 内容中包含查询词
            content_terms = set(content.split())
            content_overlap = len(query_terms & content_terms)
            score += content_overlap * 0.5

            # 原始向量分数（如果有）
            if "score" in doc:
                score += doc["score"] * 5.0

            return score

        # 计算分数并排序
        scored_docs = [(doc, calculate_score(doc)) for doc in documents]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # 返回结果
        results = []
        for doc, score in scored_docs[:top_k]:
            result = doc.copy()
            result["rerank_score"] = score
            results.append(result)

        return results


# 全局单例
_rerank_service: Optional[RerankService] = None
_simple_rerank_service: Optional[SimpleRerankService] = None


def get_rerank_service() -> RerankService:
    """获取 Rerank 服务单例"""
    global _rerank_service
    if _rerank_service is None:
        _rerank_service = RerankService()
    return _rerank_service


def get_simple_rerank_service() -> SimpleRerankService:
    """获取简单 Rerank 服务单例"""
    global _simple_rerank_service
    if _simple_rerank_service is None:
        _simple_rerank_service = SimpleRerankService()
    return _simple_rerank_service

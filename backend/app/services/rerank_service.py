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


class DashScopeRerankService:
    """阿里云 DashScope Rerank 服务"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY  # 使用 DashScope API Key
        self.model = settings.DASHSCOPE_RERANK_MODEL
        self.enabled = settings.DASHSCOPE_RERANK_ENABLED and bool(self.api_key)

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        使用 DashScope API 对文档进行重排序

        Args:
            query: 查询文本
            documents: 文档列表，每个文档必须包含 'title' 或 'content' 字段
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表，按相关性降序排列
        """
        if not self.enabled:
            logger.debug("DashScope Rerank 未启用")
            return []

        if not documents:
            return []

        try:
            # 尝试使用 DashScope SDK
            try:
                import dashscope
                from http import HTTPStatus

                # 构造文档文本列表
                doc_texts = []
                for doc in documents:
                    title = doc.get("title", "")
                    content = doc.get("content", "")
                    if title and content:
                        doc_texts.append(f"{title}\n{content[:500]}")
                    elif content:
                        doc_texts.append(content[:500])
                    else:
                        doc_texts.append(title)

                # 调用 DashScope Rerank API
                def _call_rerank():
                    dashscope.api_key = self.api_key
                    return dashscope.TextReRank.call(
                        model=self.model,
                        query=query,
                        documents=doc_texts,
                        top_n=min(top_k, len(doc_texts)),
                        return_documents=False
                    )

                response = await async_wrapper(_call_rerank)()

                if response.status_code != HTTPStatus.OK:
                    logger.error(f"DashScope Rerank API 调用失败: {response.code} - {response.message}")
                    return []

                # 构建结果列表
                results = []
                for result in response.output["results"]:
                    idx = result["index"]
                    if 0 <= idx < len(documents):
                        reranked_doc = documents[idx].copy()
                        reranked_doc["rerank_score"] = result["relevance_score"]
                        reranked_doc["rerank_source"] = "dashscope"
                        results.append(reranked_doc)

                logger.info(f"DashScope Rerank 完成，处理 {len(documents)} 个文档，返回 {len(results)} 个")
                return results

            except ImportError:
                logger.warning("dashscope SDK 未安装，尝试使用 HTTP API")
                return await self._rerank_via_http(query, documents, top_k)

        except Exception as e:
            logger.error(f"DashScope Rerank 调用失败: {e}")
            return []

    async def _rerank_via_http(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """通过 HTTP API 调用 DashScope Rerank"""
        import httpx

        # 构造文档文本列表
        doc_texts = []
        for doc in documents:
            title = doc.get("title", "")
            content = doc.get("content", "")
            if title and content:
                doc_texts.append(f"{title}\n{content[:500]}")
            elif content:
                doc_texts.append(content[:500])
            else:
                doc_texts.append(title)

        # 根据模型选择不同的 API 端点
        if self.model == "qwen3-rerank":
            url = "https://dashscope.aliyuncs.com/compatible-api/v1/reranks"
            payload = {
                "model": self.model,
                "query": query,
                "documents": doc_texts,
                "top_n": min(top_k, len(doc_texts)),
                "instruct": "Given a web search query, retrieve relevant passages that answer the query."
            }
        else:
            # gte-rerank-v2 或其他模型
            url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
            payload = {
                "model": self.model,
                "input": {
                    "query": query,
                    "documents": doc_texts
                },
                "parameters": {
                    "return_documents": False,
                    "top_n": min(top_k, len(doc_texts))
                }
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                logger.error(f"DashScope Rerank HTTP API 调用失败: {response.status_code} - {response.text}")
                return []

            data = response.json()

            # 构建结果列表
            results = []
            for result in data.get("output", {}).get("results", []):
                idx = result["index"]
                if 0 <= idx < len(documents):
                    reranked_doc = documents[idx].copy()
                    reranked_doc["rerank_score"] = result["relevance_score"]
                    reranked_doc["rerank_source"] = "dashscope"
                    results.append(reranked_doc)

            logger.info(f"DashScope Rerank (HTTP) 完成，处理 {len(documents)} 个文档，返回 {len(results)} 个")
            return results


class BgeRerankService:
    """本地 BGE Rerank 服务 - 作为兜底方案"""

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
            logger.info("BGE Rerank is disabled, skipping model loading")
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            logger.info(f"Loading BGE rerank model: {self.model_name}")

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()

            logger.info(f"BGE Rerank model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load BGE rerank model: {e}")
            self.enabled = False

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        使用本地 BGE 模型对文档进行重排序

        Args:
            query: 查询文本
            documents: 文档列表，每个文档必须包含 'title' 或 'content' 字段
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表，按相关性降序排列
        """
        if not self.enabled:
            logger.info("BGE Rerank is disabled, returning original documents")
            return documents[:top_k]

        if not documents:
            return []

        try:
            # 确保模型已加载
            self._load_model()

            if self._model is None:
                logger.warning("BGE Rerank model not loaded, returning original documents")
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
                result["rerank_source"] = "bge"
                results.append(result)

            logger.info(f"BGE Reranked {len(documents)} documents, returning top {len(results)}")
            return results

        except Exception as e:
            logger.error(f"Failed to rerank documents with BGE: {e}")
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
            result["rerank_source"] = "simple"
            results.append(result)

        return results


class HybridRerankService:
    """
    混合 Rerank 服务
    优先使用 DashScope Rerank，失败时使用本地 BGE Rerank 兜底
    """

    def __init__(self):
        self._dashscope_service = DashScopeRerankService()
        self._bge_service = BgeRerankService()
        self._simple_service = SimpleRerankService()

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        对文档进行重排序

        优先级：
        1. DashScope Rerank（如果启用且有 API Key）
        2. 本地 BGE Rerank（作为兜底）
        3. 简单规则 Rerank（最终兜底）

        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []

        # 1. 尝试使用 DashScope Rerank
        if self._dashscope_service.enabled:
            try:
                results = await self._dashscope_service.rerank(query, documents, top_k)
                if results:
                    logger.info("使用 DashScope Rerank 成功")
                    return results
            except Exception as e:
                logger.warning(f"DashScope Rerank 失败，切换到兜底方案: {e}")

        # 2. 尝试使用本地 BGE Rerank
        if self._bge_service.enabled:
            try:
                results = await self._bge_service.rerank(query, documents, top_k)
                if results:
                    logger.info("使用本地 BGE Rerank 成功")
                    return results
            except Exception as e:
                logger.warning(f"BGE Rerank 失败，切换到简单规则: {e}")

        # 3. 使用简单规则 Rerank（最终兜底）
        logger.info("使用简单规则 Rerank")
        return await self._simple_service.rerank(query, documents, top_k)


# 兼容旧代码的别名
RerankService = HybridRerankService


# 全局单例
_rerank_service: Optional[HybridRerankService] = None
_simple_rerank_service: Optional[SimpleRerankService] = None


def get_rerank_service() -> HybridRerankService:
    """获取 Rerank 服务单例（优先智谱，BGE兜底）"""
    global _rerank_service
    if _rerank_service is None:
        _rerank_service = HybridRerankService()
    return _rerank_service


def get_simple_rerank_service() -> SimpleRerankService:
    """获取简单 Rerank 服务单例"""
    global _simple_rerank_service
    if _simple_rerank_service is None:
        _simple_rerank_service = SimpleRerankService()
    return _simple_rerank_service

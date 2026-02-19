# 案例搜索性能优化方案

## 当前问题分析

经过代码分析，发现以下性能瓶颈：

### 1. 串行执行问题
```python
# 当前实现：串行执行（search_service.py:78-125）
# 1. 先执行 ES 搜索
es_results = await self.es_service.search(...)
# 2. 再执行向量搜索（需要等待 embedding 生成）
query_vector = await self.embedding_service.embed_query(query)
vector_results = await self.milvus_service.search_similar(...)
# 3. 最后执行图谱搜索
graph_results = await self.neo4j_service.search_by_tags(...)
```

**问题**：三个搜索串行执行，总时间 = T(ES) + T(向量) + T(图谱)

### 2. Embedding 阻塞
- 每次查询都需要先生成 embedding
- Embedding 服务调用有网络延迟
- 无法与 ES 搜索并行

### 3. Rerank 同步阻塞
- 所有检索完成后才执行 rerank
- Rerank 是计算密集型操作

## 优化方案

### 方案一：并行化检索（推荐）

使用 `asyncio.gather` 并行执行三个搜索：

```python
async def search_cases(self, query: str, ...):
    # 并行执行所有搜索
    es_task = self.es_service.search(...) if self.es_service else []
    vector_task = self._vector_search_with_embedding(query, ...) if query else []
    graph_task = self.neo4j_service.search_by_tags(...) if self.neo4j_service else []

    es_results, vector_results, graph_results = await asyncio.gather(
        es_task, vector_task, graph_task, return_exceptions=True
    )
```

**预期效果**：
- 总时间 ≈ max(T(ES), T(向量), T(图谱))
- 提速约 60%

### 方案二：预计算 Embedding

在案例创建/更新时预计算并存储 embedding：

```python
# 案例创建时
async def create_case(case_data):
    # 1. 保存案例到 MongoDB
    case = await self.collection.insert_one(case_data)

    # 2. 预计算 embedding 并存储
    embedding = await self.embedding_service.embed_text(case.content)
    await self.milvus_service.insert_vector(
        case_id=case.id,
        vector=embedding,
        ...
    )
```

**优势**：查询时无需计算 embedding，直接使用预存储的向量

### 方案三：异步 Rerank

将 rerank 改为流式返回：

```python
async def search_cases_stream(self, query: str, ...):
    # 1. 并行执行检索
    results = await asyncio.gather(...)

    # 2. 边检索边返回初步结果
    yield {"status": "searching", "results": results[:10]}

    # 3. 后台进行 rerank
    reranked = await self.rerank_service.rerank(...)

    # 4. 返回 rerank 后的结果
    yield {"status": "complete", "results": reranked}
```

### 方案四：结果缓存

对热门查询结果进行缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_results(query_hash):
    # 查询结果缓存
    return await self._do_search(query)
```

## 推荐实施顺序

1. **第一阶段**：并行化检索（改动小，效果明显）
2. **第二阶段**：预计算 embedding（需要数据迁移）
3. **第三阶段**：异步 rerank + 缓存（进一步优化）

## 预期性能提升

| 优化阶段 | 响应时间 | 提升幅度 |
|---------|---------|---------|
| 当前 | 3-5 秒 | - |
| 并行化 | 1-2 秒 | ~60% |
| +预计算 | 0.5-1 秒 | ~80% |
| +缓存 | <0.5 秒 | ~90% |

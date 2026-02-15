# 多检索系统 + Rerank 设计文档

## 概述

本设计文档描述了 UniKnow 案例管理系统的多路检索系统实现，结合向量检索、关键词搜索和 Rerank 重排序，提升搜索效果。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户查询                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    SearchService                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   关键词搜索     │  │    向量搜索     │                  │
│  │   (MongoDB)     │  │    (Milvus)     │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                            │
│           └────────┬───────────┘                            │
│                    ▼                                        │
│           ┌────────────────┐                                │
│           │   结果合并去重   │                                │
│           └────────┬───────┘                                │
│                    ▼                                        │
│           ┌────────────────┐                                │
│           │ Rerank 重排序   │                                │
│           │ (BGE-Reranker) │                                │
│           └────────┬───────┘                                │
│                    ▼                                        │
│           ┌────────────────┐                                │
│           │    分页返回     │                                │
│           └────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

## 组件说明

### 1. MilvusService (向量数据库服务)

**文件**: `backend/app/services/milvus_service.py`

**功能**:
- 连接管理
- 集合创建（cases 集合，1024 维向量）
- CRUD 操作
- 向量相似度搜索

**集合结构**:
```python
fields = [
    FieldSchema(name="id", dtype=VARCHAR, max_length=100, is_primary=True),
    FieldSchema(name="case_id", dtype=VARCHAR, max_length=100),
    FieldSchema(name="tenant_id", dtype=VARCHAR, max_length=100),
    FieldSchema(name="title", dtype=VARCHAR, max_length=500),
    FieldSchema(name="content", dtype=VARCHAR, max_length=8000),
    FieldSchema(name="case_type", dtype=VARCHAR, max_length=50),
    FieldSchema(name="category_id", dtype=VARCHAR, max_length=100),
    FieldSchema(name="embedding", dtype=FLOAT_VECTOR, dim=1024),
]
```

### 2. RerankService (重排序服务)

**文件**: `backend/app/services/rerank_service.py`

**功能**:
- 加载 BAAI/bge-reranker-v2-m3 模型
- 对搜索结果进行重排序
- 提供简单规则重排序作为后备

**模型**:
- BGE-Reranker-v2-m3：多语言支持，适合中英文场景
- 运行设备：CPU（可配置为 CUDA/MPS）

### 3. SearchService (混合搜索服务)

**文件**: `backend/app/services/search_service.py`

**搜索流程**:
1. 关键词搜索（MongoDB 正则匹配）
2. 向量搜索（Milvus 余弦相似度）
3. 结果合并去重
4. Rerank 重排序
5. 分页返回

### 4. CaseService (案例服务 - 集成向量同步)

**文件**: `backend/app/services/case_service.py`

**向量同步逻辑**:
- 创建已发布案例时：自动向量化并存储到 Milvus
- 更新已发布案例时：更新 Milvus 中的向量
- 删除案例时：从 Milvus 删除向量
- 发布案例时：向量化并存储
- 取消发布时：从 Milvus 删除

## Docker 服务

**文件**: `docker-compose.yml`

新增服务:
- `etcd`: Milvus 元数据存储
- `minio`: Milvus 对象存储
- `milvus`: 向量数据库

端口映射:
- Milvus: 19530 (gRPC), 9091 (健康检查)
- Minio: 9000 (API), 9001 (控制台)

## 配置

**文件**: `backend/app/core/config.py`

```python
# Milvus 配置
MILVUS_HOST: str = "localhost"
MILVUS_PORT: int = 19530
MILVUS_COLLECTION: str = "cases"

# Rerank 配置
RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
RERANK_DEVICE: str = "cpu"
RERANK_ENABLED: bool = True

# 向量维度
EMBEDDING_DIMENSION: int = 1024
```

## 数据迁移

**脚本**: `backend/scripts/migrate_to_milvus.py`

使用方法:
```bash
cd backend
source .venv/bin/activate
python scripts/migrate_to_milvus.py --tenant-id default --batch-size 10
```

## 依赖

**文件**: `backend/requirements.txt`

新增:
- `pymilvus==2.3.3`: Milvus Python SDK
- `transformers==4.36.2`: HuggingFace Transformers
- `torch==2.1.2`: PyTorch

## 后续扩展

### 阶段 2: Elasticsearch

- 添加 ES 服务
- 实现全文检索
- 数据同步逻辑

### 阶段 3: Neo4j 图谱

- 添加 Neo4j 服务
- 实现图谱构建
- 图谱检索逻辑

## 验证方案

1. 启动服务:
   ```bash
   docker-compose up -d etcd minio milvus
   ```

2. 运行迁移脚本:
   ```bash
   python scripts/migrate_to_milvus.py
   ```

3. 测试搜索接口:
   - 验证向量搜索返回相关结果
   - 验证 Rerank 后结果排序更合理

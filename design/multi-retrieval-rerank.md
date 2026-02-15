# 多检索系统 + Rerank 设计文档

## 概述

本设计文档描述了 UniKnow 案例管理系统的多路检索系统实现，结合 ES 全文检索、向量检索、图谱检索和 Rerank 重排序，提升搜索效果。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户查询                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    SearchService                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  ES 全文检索 │  │  向量搜索   │  │  图谱检索   │         │
│  │(Elasticsearch)│ │  (Milvus)  │  │  (Neo4j)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│                 ┌────────────────┐                          │
│                 │   结果合并去重   │                          │
│                 │  (加权融合分数)  │                          │
│                 └────────┬───────┘                          │
│                          ▼                                  │
│                 ┌────────────────┐                          │
│                 │ Rerank 重排序   │                          │
│                 │ (BGE-Reranker) │                          │
│                 └────────┬───────┘                          │
│                          ▼                                  │
│                 ┌────────────────┐                          │
│                 │    分页返回     │                          │
│                 └────────────────┘                          │
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

### 2. ElasticsearchService (全文检索服务)

**文件**: `backend/app/services/es_service.py`

**功能**:
- 索引管理
- 文档索引/更新/删除
- 全文搜索（支持 ik 中文分词）

### 3. Neo4jService (图谱服务)

**文件**: `backend/app/services/neo4j_service.py`

**功能**:
- 图节点管理（案例、标签、分类）
- 关系管理（案例-标签、案例-分类）
- 基于关系的检索

### 4. RerankService (重排序服务)

**文件**: `backend/app/services/rerank_service.py`

**功能**:
- 加载 BAAI/bge-reranker-v2-m3 模型
- 对搜索结果进行重排序
- 提供简单规则重排序作为后备

### 5. SearchService (多路检索服务)

**文件**: `backend/app/services/search_service.py`

**搜索流程**:
1. 并行执行三路检索（ES、向量、图谱）
2. 结果合并去重
3. Rerank 重排序
4. 分页返回

### 6. CaseService (案例服务 - 多数据源同步)

**文件**: `backend/app/services/case_service.py`

**同步逻辑**:
- 创建/更新已发布案例时：同步到 Milvus、ES、Neo4j
- 删除案例时：从所有数据源删除
- 发布/取消发布时：同步/删除数据

## Docker 服务

**文件**: `docker-compose.yml`

服务列表:
- `etcd`: Milvus 元数据存储
- `minio`: Milvus 对象存储
- `milvus`: 向量数据库
- `elasticsearch`: 全文检索引擎
- `neo4j`: 图数据库

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

# Elasticsearch 配置
ES_HOST: str = "localhost"
ES_PORT: int = 9200
ES_INDEX: str = "cases"
ES_ENABLED: bool = True

# Neo4j 配置
NEO4J_URI: str = "bolt://localhost:7687"
NEO4J_USER: str = "neo4j"
NEO4J_PASSWORD: str = "uniknow123"
NEO4J_ENABLED: bool = True

# 向量维度
EMBEDDING_DIMENSION: int = 1024
```

## 依赖

**文件**: `backend/requirements.txt`

- `pymilvus==2.3.3`: Milvus Python SDK
- `transformers==4.36.2`: HuggingFace Transformers
- `torch==2.1.2`: PyTorch
- `elasticsearch==8.11.0`: Elasticsearch Python SDK
- `neo4j==5.15.0`: Neo4j Python Driver

## 使用方法

```bash
# 1. 启动所有服务
docker-compose up -d

# 2. 安装依赖
cd backend && uv sync

# 3. 运行数据迁移（可选）
source .venv/bin/activate
python scripts/migrate_to_milvus.py

# 4. 启动后端
uvicorn app.main:app --reload --port 8000
```

## 检索策略

### 综合分数计算

```
combined_score = 0.4 * ES_score + 0.4 * Vector_score + 0.2 * Graph_score
```

### 回退策略

当所有检索服务不可用时，回退到 MongoDB 关键词搜索。

## 验证方案

1. 启动服务: `docker-compose up -d`
2. 检查服务健康状态
3. 测试搜索接口
4. 验证 Rerank 效果

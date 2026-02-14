# AGENTS.md

本文件为 Codex/ChatGPT 等编码代理提供本仓库的协作约定与使用指引。

## 项目概览

UniKnow 是面向内部客服的案例管理知识库 SaaS，核心能力：
- 案例管理：CRUD、审批流程、模板、内部/外部案例类型
- 案例搜索：座席搜索与用户搜索（仅外部案例）
- GraphRag 问答：基于 LangGraph 的智能问答

## 常用命令

### 后端（FastAPI）
```bash
cd backend

# 创建虚拟环境并安装依赖（uv）
uv venv
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，补充 OPENAI_API_KEY

# 启动开发服务（端口 8000）
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 前端（Vue 3 + Vite）
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务（端口 80）
npm run dev

# 生产构建
npm run build

# 代码检查
npm run lint
```

### Docker
```bash
# 启动全部服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 架构概览

### 后端（FastAPI + LangGraph）
```
app/
├── api/              # REST API endpoints
│   ├── case.py       # Case CRUD operations
│   ├── search.py     # Search endpoints
│   ├── approval.py   # Approval workflow
│   └── operation.py  # Statistics/logs
├── core/
│   ├── config.py     # Pydantic settings (MongoDB, Redis, OpenAI)
│   └── security.py   # JWT auth dependencies
├── graph/            # LangGraph workflow for GraphRag
│   ├── state.py      # GraphState model (question, docs, entities, answer)
│   └── workflow.py   # StateGraph: extract -> reformulate -> retrieve -> generate -> evaluate
├── nodes/            # LangGraph nodes
│   ├── search_node.py # retrieve_documents, extract_entities
│   ├── rag_node.py    # generate_answer, evaluate_answer
│   └── case_node.py   # validate_case, process_approval
├── models/           # MongoDB document models (Case, Approval, Template, etc.)
├── schemas/          # Pydantic request/response models
├── services/         # Business logic layer
│   ├── case_service.py
│   ├── search_service.py  # Hybrid vector + keyword search
│   └── graph_service.py   # Invokes LangGraph workflow
├── tools/
│   └── embedding.py  # OpenAI text-embedding-3-small
└── main.py           # FastAPI app factory
```

GraphRag 关键流程：
1. `extract_entities`（提取关键词）
2. `reformulate_query`（改写查询）
3. `retrieve_documents`（检索案例）
4. `generate_answer`（GPT-4 生成回答）
5. `evaluate_answer`（置信度评估）

### 前端（Vue 3 + Element Plus）
```
src/
├── views/            # Page components
│   ├── login/        # Authentication
│   ├── layout/       # Main layout with sidebar navigation
│   ├── dashboard/    # Statistics overview
│   ├── cases/        # Case CRUD pages
│   ├── search/       # Search interface
│   ├── qa/           # Chat interface for GraphRag Q&A
│   ├── approvals/    # Approval management
│   └── operation/    # Statistics dashboard
├── router/           # Vue Router (8 routes)
├── stores/           # Pinia stores (user auth)
├── services/
│   ├── api.js        # Axios instance with interceptors
│   └── case.js       # API wrappers (caseApi, searchApi, approvalApi, qaApi)
├── assets/styles/    # SCSS variables and common styles
└── App.vue           # Root component with Element Plus config
```

## API 端点

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cases` | Create case |
| GET | `/api/v1/cases/{id}` | Get case details |
| PUT | `/api/v1/cases/{id}` | Update case |
| DELETE | `/api/v1/cases/{id}` | Delete case |
| GET | `/api/v1/cases` | List cases (paginated) |
| POST | `/api/v1/search/cases` | Seat search |
| GET | `/api/v1/search/user` | User search (external only) |
| POST | `/api/v1/approvals/{id}/approve` | Approve case |
| POST | `/api/v1/approvals/{id}/reject` | Reject case |
| POST | `/api/v1/graph/ask` | GraphRag Q&A |

## 重要实现说明

1. 数据库：MongoDB（Motor 异步驱动 `AsyncIOMotorClient`）
2. 缓存：Redis（已配置但暂未集成）
3. AI：GPT-4 生成回答，`text-embedding-3-small` 生成向量
4. 案例类型：`internal`（内部）与 `external`（外部）
5. 案例状态：`draft` → `pending_approval` → `approved`/`rejected` → `published`
6. 认证：Bearer Token，API 路由中通过 `Depends(get_current_user)`

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UniKnow is a case management knowledge base SaaS system for internal customer service. It provides:
- **Case Management**: CRUD operations, approval workflows, templates, internal/external case types
- **Case Search**: Seat search and user search (external cases only)
- **GraphRag Q&A**: AI-powered question answering using LangGraph

## Commands

### Quick Start (启动所有服务)

```bash
# 1. 启动 Docker Desktop（如果未运行）
open -a Docker

# 2. 启动 Docker 容器（MongoDB, Redis 等）
docker-compose up -d

# 3. 启动后端（新终端窗口）
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# 4. 启动前端（新终端窗口）
cd frontend && npm run dev
```

服务地址：
- 前端：http://localhost:80
- 后端：http://127.0.0.1:8000

### Backend (FastAPI)
```bash
cd backend

# Create virtual environment and install dependencies with uv
uv venv
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Activate virtual environment and run
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend

# Install dependencies
npm install

# Run development server (port 80)
npm run dev

# Build for production
npm run build

# Lint files
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

### Backend (FastAPI + LangGraph)

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

**Key Flow - GraphRag Q&A:**
1. User question → `extract_entities` (extract keywords)
2. → `reformulate_query` (improve query)
3. → `retrieve_documents` (search cases)
4. → `generate_answer` (GPT-4 with context)
5. → `evaluate_answer` (confidence check)

### Frontend (Vue 3 + Element Plus)

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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cases` | Create case |
| GET | `/api/v1/cases/{id}` | Get case details |
| PUT | `/api/v1/cases/{id}` | Update case |
| DELETE | `/api/v1/cases/{id}` | Delete case |
| GET | `/api/v1/cases` | List cases (paginated) |
| POST | `/api/v1/cases/{id}/approve` | Approve case by ID |
| POST | `/api/v1/cases/{id}/reject` | Reject case by ID |
| POST | `/api/v1/search/cases` | Seat search |
| GET | `/api/v1/search/user` | User search (external only) |
| GET | `/api/v1/approvals` | List approvals (status: pending/approved/rejected/processed) |
| POST | `/api/v1/approvals/{id}/approve` | Approve case |
| POST | `/api/v1/approvals/{id}/reject` | Reject case |
| POST | `/api/v1/graph/ask` | GraphRag Q&A (streaming) |

## Task Development Workflow (任务开发流程)

项目使用 `TODO.md` 管理待办任务，按以下流程循环执行：

```
1. 读取 TODO.md 获取任务列表
      ↓
2. 取第一个未完成任务进行开发
      ↓
3. 开发完成后自测验证（启动服务，使用 agent-browser 自动化测试）
      ↓
4. 更新 TODO.md 标记任务完成
      ↓
5. 提交代码到 GitHub
      ↓
6. 清空上下文，回到步骤 1 取下一个任务
      ↓
... 循环直到所有任务完成 ...
      ↓
全量回归测试
```

**注意事项**：
- 每次只处理一个任务，完成后提交
- 提交前必须自测验证功能正常
- 任务完成后及时更新 TODO.md 勾选状态
- 设计产出保存到 `design/` 文件夹中（如功能设计文档、UI 设计稿等）

## Important Implementation Notes

1. **Database**: MongoDB with Motor async driver (`AsyncIOMotorClient`)
2. **Cache**: Redis for caching (configured but not yet integrated)
3. **AI**: OpenAI GPT-4 for answer generation, text-embedding-3-small for vectors (via Alibaba DashScope)
4. **Case Types**: `internal` (staff only) vs `external` (public)
5. **Case Status**: `draft` → `pending_approval` → `approved`/`rejected` → `published`
6. **Authentication**: Bearer token via `Depends(get_current_user)` in API routes
7. **RBAC Permissions**:
   - `admin`: Full access - create, edit, delete, approve/reject cases
   - `agent`: Create and edit cases, requires approval for publishing
   - `user`: Read-only access
8. **Streaming Q&A**: GraphRag uses LangGraph's `astream` for real-time streaming with typing effect

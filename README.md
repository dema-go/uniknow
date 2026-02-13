# UniKnow 案例管理系统

UniKnow 是公司内部客服使用的知识库 SaaS 服务，支持案例管理、智能搜索和 GraphRag 智能问答。

## 功能特性

### 案例管理
- 案例创建、编辑、删除
- 案例审批流程
- 案例模板支持
- 对内/对外案例区分
- Markdown 编辑器（支持富文本切换）
- TinyMCE 富文本编辑器
- 代码高亮和预览

### 权限管理
- JWT 认证
- 基于角色的访问控制 (RBAC)
  - 管理员 (admin): 直接发布案例，无需审批
  - 维护员 (agent): 创建案例需要审批
  - 普通用户 (user): 只读访问

### 案例使用
- 坐席搜索
- 用户搜索（仅对外案例）
- GraphRag 智能问答

### 整体运营
- 案例统计
- 问答统计
- 操作日志

## 技术栈

### 前端
- Vue 3 + Vite
- Pinia 状态管理
- Vue Router
- Element Plus
- md-editor-v3 (Markdown 编辑器)
- TinyMCE (富文本编辑器)
- marked (Markdown 渲染)

### 后端
- FastAPI
- LangGraph + LangChain
- MongoDB
- Redis
- 阿里云 DashScope (通义千问 + Embedding)
- JWT 认证 (python-jose)
- MongoDB 异步驱动 (Motor)

## 项目结构

```
uniknow/
├── backend/               # 后端项目
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── graph/        # LangGraph 工作流
│   │   ├── models/       # 数据模型
│   │   ├── nodes/        # Graph 节点
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务逻辑
│   │   └── tools/        # 工具函数
│   └── tests/
├── frontend/             # 前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态
│   │   ├── services/     # API 服务
│   │   └── assets/       # 静态资源
│   └── public/
└── docker-compose.yml    # Docker 编排
```

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.10+
- uv (Python 包管理器)
- MongoDB 7.0+
- Redis 7+

### 后端启动

```bash
cd backend

# 安装 uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
uv sync

# 复制环境变量
cp .env.example .env
# 编辑 .env 文件，配置阿里云 DashScope API Key:
# OPENAI_API_KEY=sk-xxxxx
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# EMBEDDING_MODEL=text-embedding-v2

# 启动服务
source .venv/bin/activate
uvicorn app.main:app --reload
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 直接发布案例，无需审批 |
| 维护员 | agent | agent123 | 创建案例需要审批 |
| 普通用户 | user | user123 | 只读访问 |

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## API 文档

### 认证
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出

### 案例管理
- `POST /api/v1/cases` - 创建案例
- `GET /api/v1/cases/{id}` - 获取案例详情
- `PUT /api/v1/cases/{id}` - 更新案例
- `DELETE /api/v1/cases/{id}` - 删除案例
- `GET /api/v1/cases` - 案例列表

### 搜索
- `POST /api/v1/search/cases` - 坐席搜索
- `GET /api/v1/search/user` - 用户搜索

### 审批
- `GET /api/v1/approvals` - 审批列表（支持 status: pending/approved/rejected/processed）
- `POST /api/v1/approvals` - 创建审批
- `POST /api/v1/approvals/{id}/approve` - 通过审批
- `POST /api/v1/approvals/{id}/reject` - 拒绝审批
- `POST /api/v1/cases/{id}/approve` - 通过案例审批（基于案例 ID）
- `POST /api/v1/cases/{id}/reject` - 拒绝案例审批（基于案例 ID）

### 智能问答
- `POST /api/v1/graph/ask` - GraphRag 问答

## License

MIT

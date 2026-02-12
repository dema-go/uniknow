.
├── app/
│   ├── api/              # API 路由
│   │   ├── __init__.py
│   │   ├── case.py       # 案例相关接口
│   │   ├── search.py     # 搜索相关接口
│   │   ├── approval.py   # 审批相关接口
│   │   └── operation.py  # 运营统计接口
│   ├── core/             # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理
│   │   └── security.py   # 安全认证
│   ├── graph/            # LangGraph 图定义
│   │   ├── __init__.py
│   │   ├── state.py      # 图状态定义
│   │   └── workflow.py   # 工作流编排
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   └── database.py   # 数据库模型
│   ├── nodes/            # LangGraph 节点
│   │   ├── __init__.py
│   │   ├── case_node.py  # 案例处理节点
│   │   ├── search_node.py # 搜索处理节点
│   │   └── rag_node.py    # RAG 处理节点
│   ├── schemas/          # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── case.py       # 案例相关 Schema
│   │   └── common.py     # 通用 Schema
│   ├── services/         # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── case_service.py
│   │   ├── search_service.py
│   │   ├── approval_service.py
│   │   └── graph_service.py
│   ├── tools/            # 工具函数
│   │   ├── __init__.py
│   │   └── embedding.py
│   └── main.py           # FastAPI 入口
├── tests/                # 测试文件
├── requirements.txt      # 依赖
└── .env                  # 环境变量

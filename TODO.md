# 待办事项

- [x] 增加案例模版功能，即内置几个通用的格式模版，用户点击时自动将格式渲染到markdown/富文本编辑器上。
    具体样式：
        - 在编辑器页面右侧增加一个悬浮栏，点击后展开有多个按钮选项：
            - 搜索
            - 案例模版
            - 案例评分
            - 案例润色
            等
        - 点击案例模版后，弹出模版选择框，用户选择后，自动将模版渲染到编辑器中。
- [x] 案例搜索区分对内、对外
- [x] 案例搜索引入ES检索、向量检索、图谱检索，对三者返回的数据进行rerank
    - [x] 集成 Milvus 向量数据库
    - [x] 集成 BGE-Reranker 重排序
    - [x] 集成 Elasticsearch 全文检索
    - [x] 集成 Neo4j 图谱检索
    - [x] 实现多路检索 + Rerank

- [x] 案例模版点击后没有反应，并没有出现模版的选项
    - **原因**: Docker 容器中的前端代码是旧版本，未包含 EditorSidebar 组件
    - **解决**: 重新构建前端 Docker 镜像 (`docker-compose build frontend`)

- [x] 参考WeKnora项目可以区分出案例形式，大体分为两种：FAQ和文档。文档可以存到MinIO上。WeKnora的代码在～/WeKnora中，可以参考
    - **后端实现**:
        - 新增 `CaseForm` 枚举（faq/document）和文档相关字段
        - 创建 MinIO 存储服务 (`storage_service.py`)
        - 创建文件上传/下载 API (`file.py`)
    - **前端实现**:
        - 案例创建页面支持形式选择和文件上传
        - 案例详情页支持文档下载
        - 案例列表页支持形式筛选

- [x] 重排序换成智谱的rerank模型，可以上网查找对应的文档，当前使用的模型可以作为智谱rerank失效时的兜底方案
    - **实现**:
        - 新增 `ZhipuRerankService` 类，使用智谱 AI GLM-rerank 模型
        - 新增 `HybridRerankService` 混合服务，优先级：智谱 > 本地 BGE > 简单规则
        - 更新配置项：`ZHIPU_API_KEY`、`ZHIPU_RERANK_MODEL`、`ZHIPU_RERANK_ENABLED`
        - 添加 zhipuai SDK 依赖
    - **注意**: 需要在 `.env` 中配置 `ZHIPU_API_KEY` 才能启用智谱 Rerank
- [ ] ES 连接错误: 后端无法连接到 Elasticsearch（localhost:9200），排查并修复问题，我在docker中看到es是正常启动的
- [ ] Milvus API Key 错误: OpenAI API Key 配置问题，将milvus改造为使用阿里云的apikey，apikey在.env中
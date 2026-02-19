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

- [x] 重排序换成阿里云 DashScope 的 Rerank 模型，当前使用的 BGE 模型可以作为兜底方案
    - **实现**:
        - 新增 `DashScopeRerankService` 类，使用阿里云 DashScope qwen3-rerank 模型
        - 新增 `HybridRerankService` 混合服务，优先级：DashScope > 本地 BGE > 简单规则
        - 更新配置项：`DASHSCOPE_RERANK_MODEL`、`DASHSCOPE_RERANK_ENABLED`
        - 添加 dashscope SDK 依赖
    - **注意**: 使用 `.env` 中的 `OPENAI_API_KEY` 作为 DashScope API Key
- [x] ES 连接错误: 后端无法连接到 Elasticsearch（localhost:9200），排查并修复问题，我在docker中看到es是正常启动的
    - **原因**: elasticsearch Python 客户端 9.x 与服务端 8.x 版本不兼容
    - **解决**: 降级 elasticsearch 客户端到 8.x 版本（8.19.3）
    - **修复**: 更新 es_service.py API 调用，适配 elasticsearch 8.x 的参数格式
- [x] Milvus API Key 错误: OpenAI API Key 配置问题，将milvus改造为使用阿里云的apikey，apikey在.env中
    - **解决**: 已使用阿里云 DashScope 的 OpenAI 兼容模式（OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1）
    - **修复**: 更新 EMBEDDING_MODEL 为 text-embedding-v3，维度为 1024
    - **验证**: Milvus 向量插入和搜索功能正常工作

- [x] ~~尝试使用 Zvec 替换 Milvus~~ (已回退)
    - **原因**: Zvec 要求 Python 3.10-3.12，项目使用 Python 3.13 不兼容
    - **状态**: 已回退到 Milvus，所有代码恢复原状

- [x] 搜索和问答功能修复
    - **问题**: ES 连接 localhost:9200 失败（容器内应连接 elasticsearch:9200），OPENAI_API_KEY 未传入
    - **修复**:
        - 在 config.py 添加 ES_URL 配置项支持完整 URL
        - 在 es_service.py 中支持 ES_URL 优先于 ES_HOST:ES_PORT
        - 在 docker-compose.yml 添加 ES_URL=http://elasticsearch:9200
        - 添加 .env 文件到项目根目录供 docker-compose 读取 OPENAI_API_KEY
        - 添加 dashscope SDK 依赖到 requirements.txt
        - 修复 es_service.py 中的日志输出错误（self.port 不存在）
    - **验证**: 搜索和智能问答功能正常工作

- [x] 案例模版功能点击后没有反应，出现的模版内容预览不到，无法选择
    - **原因**: Docker 容器中的前端代码是旧版本，未包含 EditorSidebar 和 TemplateDialog 组件
    - **解决**: 重新构建前端 Docker 镜像 (`docker-compose build frontend && docker-compose up -d frontend`)
    - **验证**: 测试通过，模版选择框正常显示，模版内容成功插入编辑器
- [x] 智能问答中是否可以把使用到的具体案例展示出来，类似于现在大模型问答一样可以展示引用的知识来源
    - **修复**: 前端 sources 解析逻辑错误（从 `parsed.sources` 改为 `parsed.type === 'source'`）
    - **改进**: 当 title 为空时显示 "未命名案例"，支持 case_id 字段
- [ ] 案例搜索的性能很慢，优化下搜索算法提升性能，先给出优化计划
    ## 搜索性能优化计划

    ### 当前问题分析
    1. **串行执行**：ES、向量、图谱搜索串行执行，而非并行
    2. **Embedding 阻塞**：需要等待 embedding 生成后才能进行向量搜索
    3. **Rerank 同步**：rerank 操作同步执行，阻塞响应

    ### 优化方案
    1. **并行化检索**：使用 `asyncio.gather` 并行执行 ES、向量、图谱搜索
    2. **预计算 embedding**：在索引时预计算并存储 embedding，查询时直接使用
    3. **异步 rerank**：rerank 也改为异步执行
    4. **缓存结果**：对热门查询结果进行缓存
    5. **结果流式返回**：边检索边返回结果，无需等待所有检索完成

    ### 预期效果
    - 搜索响应时间从 3-5 秒降低到 1 秒以内
    - 并行执行可提速约 60%
- [ ] 文档类型案例实现在线预览功能，先给出技术选型和实现方案
    ## 文档在线预览技术选型和实现方案

    ### 技术选型

    | 文档类型 | 推荐方案 | 优点 | 缺点 |
    |----------|----------|------|------|
    | PDF | PDF.js 前端渲染 | 开源免费、性能好、无需后端转换 | 需要加载 PDF.js |
    | Word/Excel/PPT | 微软 Office Online / 永中DCS | 功能完整、格式保真 | 需要付费服务 |
    | 纯文本/TXT | 前端直接显示 | 简单、无需转换 | - |
    | Markdown | 前端渲染 | 开源免费 | - |

    ### 推荐实现方案

    1. **PDF 文件**：
       - 后端：添加 `/api/v1/files/{bucket}/{object}/preview` 接口，返回 PDF 文件
       - 前端：使用 `<embed>` 或 PDF.js 组件预览

    2. **Office 文档**：
       - 方案一：集成 永中DCS（国产免费）
       - 方案二：使用 iframe 嵌入微软 Office Online（需付费）
       - 方案三：后端使用 libreoffice 转换为 PDF

    3. **文本文件**：
       - 后端：直接返回文本内容
       - 前端：使用 `<pre>` 标签显示

    ### 实现步骤
    1. 后端添加文件预览 API（支持 PDF 和文本）
    2. 前端添加文档预览组件
    3. 案例详情页添加"预览"按钮
    4. Office 文档考虑第三方服务集成
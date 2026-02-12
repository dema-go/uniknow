# 更新日志

## [未发布]

### 修复
- 修复前端无限刷新问题（移除layout中导致组件重复挂载的transition）
- 添加智能问答API路由 (`/api/v1/graph/ask`)
- 修复GraphRag工作流状态管理（从BaseModel迁移到TypedDict）
- 修复embedding服务以正确调用阿里云DashScope OpenAI兼容模式API
- 改进前端问答页面错误处理

### 变更
- embedding服务改用AsyncOpenAI客户端，支持阿里云DashScope
- 更新API配置支持阿里云通义千问模型（qwen-plus）
- 更新embedding模型配置为text-embedding-v2

## [1.0.0] - 初始版本

### 功能
- 案例管理（创建、编辑、删除）
- 案例审批流程
- 坐席搜索和用户搜索
- GraphRag智能问答
- 运营统计和操作日志

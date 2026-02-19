# 文档在线预览技术选型方案

## 需求分析

案例管理系统需要支持文档类型案例的在线预览功能，支持的文档格式包括：
- PDF
- Word (doc, docx)
- Excel (xls, xlsx)
- PPT (ppt, pptx)
- 纯文本 (txt)
- Markdown (md)

## 技术方案对比

### 1. PDF 预览

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| PDF.js 前端渲染 | 开源免费、性能好、无需后端转换 | 需要加载 PDF.js 库 | ✅ |
| 后端转图片 + 前端展示 | 兼容性 好 | 需要后端处理、转换慢 | |
| `<embed>` 标签 | 简单 | 依赖浏览器 PDF 插件 | |

**推荐方案**：PDF.js
- 社区成熟，文档丰富
- 支持移动端
- 无需后端转换

### 2. Office 文档预览

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 永中DCS | 国产免费、功能完整 | 需要申请账号 | ✅ |
| 微软 Office Online | 功能完整、格式保真 | 需要付费 365 订阅 | |
| iframe 嵌入 | 实现简单 | 需要公网访问 | |
| 后端转换为 PDF | 可离线 | 需要 libreoffice 服务 | |
| docx-preview.js | 前端渲染 docx | 仅支持 docx | |

**推荐方案**：永中DCS（免费额度足够）
- 提供免费 API
- 支持 Word/Excel/PPT
- 支持多种预览模式

### 3. 文本文件预览

| 方案 | 优点 | 缺点 |
|------|------|------|
| 后端直接返回文本 | 实现简单 | - |
| Base64 编码返回 | 避免编码问题 | 文件大时性能差 |

**推荐方案**：后端直接返回文本内容，前端使用 `<pre>` 标签展示

### 4. Markdown 预览

| 方案 | 优点 | 缺点 |
|------|------|------|
| marked.js | 轻量级 | 功能基础 |
| markdown-it | 功能丰富、插件多 | 需要配置 |
| 前端组件 | 已有 md-editor-v3 | - |

**推荐方案**：直接使用现有的 md-editor-v3 组件渲染

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                         前端                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ PDF.js      │  │ 永中DCS API │  │ <pre> 文本展示  │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         后端                                  │
│  ┌─────────────────────┐  ┌──────────────────────────┐    │
│  │ /api/v1/files/preview │  │ /api/v1/files/download  │    │
│  │ (返回文件内容/URL)     │  │ (返回完整文件)          │    │
│  └─────────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MinIO 存储                              │
└─────────────────────────────────────────────────────────────┘
```

## API 设计

### 预览接口

```python
@router.get("/{bucket}/{object_name:path}/preview")
async def preview_file(
    bucket: str,
    object_name: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    预览文件

    返回：
    - PDF/文本：直接返回内容，前端渲染
    - Office：返回第三方预览 URL
    """
    storage = get_storage_service()

    # 根据文件类型返回不同内容
    if is_pdf(object_name):
        # 返回 PDF 内容
        content, content_type = storage.get_file(...)
        return Response(content=content, media_type="application/pdf")

    elif is_office(object_name):
        # 返回永中DCS预览URL
        preview_url = await get_yongzhong_preview_url(object_name)
        return {"preview_url": preview_url}

    elif is_text(object_name):
        # 返回文本内容
        content, _ = storage.get_file(...)
        return Response(content=content, media_type="text/plain")
```

## 前端实现

### 预览组件

```vue
<template>
  <el-dialog v-model="previewVisible" title="文档预览" width="80%">
    <!-- PDF 预览 -->
    <iframe v-if="isPDF" :src="pdfUrl" class="preview-frame" />

    <!-- Office 文档 -->
    <iframe v-else-if="isOffice" :src="previewUrl" class="preview-frame" />

    <!-- 文本 -->
    <pre v-else-if="isText" class="text-preview">{{ content }}</pre>
  </el-dialog>
</template>
```

## 实施计划

### 第一阶段：PDF 预览
1. 后端添加 `/preview` 接口
2. 前端添加 PDF 预览组件
3. 案例详情页添加"预览"按钮

### 第二阶段：文本预览
1. 后端支持文本文件直接返回
2. 前端使用 `<pre>` 标签展示

### 第三阶段：Office 预览
1. 申请永中DCS账号
2. 集成永中DCS API
3. 支持 Word/Excel/PPT 预览

## 成本估算

| 项目 | 成本 |
|------|------|
| PDF.js | 免费 (开源) |
| 永中DCS | 免费 (有额度限制) |
| 微软 Office 365 | ¥398/年 (可选) |

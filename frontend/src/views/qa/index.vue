<template>
  <div class="qa-page-modern">
    <el-container class="chat-layout">
      <!-- Main Chat Area -->
      <el-main class="chat-main">
        <div class="chat-header">
          <div class="header-info">
            <div class="ai-avatar">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="ai-meta">
              <h3>UniKnow 智能助手</h3>
              <p>基于 GraphRAG 技术，为您提供精准解答</p>
            </div>
          </div>
        </div>

        <div class="messages-container" ref="chatContainer">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message-wrapper', msg.role]"
          >
            <div class="message-bubble">
              <div class="avatar-col" v-if="msg.role === 'assistant'">
                <el-avatar :size="40" class="assistant-avatar" icon="Cpu" />
              </div>

              <div class="content-col">
                <div class="bubble-content">
                  <div class="text" v-html="formatMessage(msg.content)"></div>
                  <!-- 思考状态指示器 -->
                  <div v-if="msg.thinking" class="thinking-indicator">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>{{ msg.thinking }}</span>
                  </div>
                </div>

                <div class="sources-panel" v-if="msg.sources && msg.sources.length">
                  <div class="sources-header"><el-icon><Link /></el-icon> 参考来源</div>
                  <div class="source-tags">
                     <el-tag
                      v-for="source in msg.sources"
                      :key="source.id"
                      class="source-tag"
                      effect="plain"
                      @click="viewSource(source.id)"
                    >
                      {{ source.title }}
                    </el-tag>
                  </div>
                </div>
              </div>

               <div class="avatar-col" v-if="msg.role === 'user'">
                <el-avatar :size="40" class="user-avatar" icon="UserFilled" />
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-container">
          <div class="input-wrapper">
            <el-input
              v-model="question"
              type="textarea"
              :rows="2"
              placeholder="请输入您的问题（Enter 发送）"
              resize="none"
              class="chat-input"
              @keydown.enter.prevent="handleAsk"
              :disabled="loading"
            />
            <div class="input-actions">
              <div class="hint">Shift + Enter 换行</div>
              <el-button type="primary" circle class="send-btn" @click.prevent="handleAsk" :loading="loading">
                <el-icon><Position /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-main>

      <!-- Right Sidebar: Quick Actions & History -->
      <el-aside width="320px" class="chat-sidebar">
        <el-card class="sidebar-card tips-card" shadow="never">
          <template #header>
            <div class="card-title"><el-icon><Lightning /></el-icon> 常见问题</div>
          </template>
          <div class="quick-tags">
            <div
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              @click="question = q"
            >
              {{ q }}
            </div>
          </div>
        </el-card>

        <el-card class="sidebar-card stats-card" shadow="never">
           <template #header>
            <div class="card-title"><el-icon><DataAnalysis /></el-icon> 今日数据</div>
          </template>
           <div class="mini-stats">
            <div class="stat-row">
              <span class="label">今日提问</span>
              <span class="value">128</span>
            </div>
             <div class="stat-row">
              <span class="label">解决率</span>
              <span class="value high">98%</span>
            </div>
           </div>
        </el-card>
      </el-aside>
    </el-container>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const chatContainer = ref(null)
const question = ref('')
const loading = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是 UniKnow 智能助手。基于先进的 GraphRAG 技术，我可以回答关于公司案例、流程规范等各类问题。'
  }
])

const quickQuestions = [
  '如何重置用户密码？',
  '查看最新的财务报表导出流程',
  '遇到恶意IP攻击怎么处理？',
  '退款审批需要哪些材料？',
  '产品核心功能介绍'
]

const formatMessage = (content) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

const handleAsk = async (e) => {
  // Allow Shift+Enter for new line
  if (e && e.shiftKey) return

  if (!question.value.trim() || loading.value) return

  messages.value.push({
    role: 'user',
    content: question.value
  })

  const userQuestion = question.value
  question.value = ''
  loading.value = true

  // 添加一个空的助手消息用于流式更新
  const assistantMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    thinking: '正在思考...',
    sources: []
  })

  scrollToBottom()

  try {
    const response = await fetch('/api/v1/graph/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ question: userQuestion })
    })

    if (!response.ok) {
      throw new Error('网络请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() // 保留未完成的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          try {
            const parsed = JSON.parse(data)

            // 处理不同类型的事件
            if (parsed.message === '开始处理问题') {
              messages.value[assistantMessageIndex].thinking = '正在分析问题...'
            } else if (parsed.text) {
              // 内容更新
              messages.value[assistantMessageIndex].content += parsed.text
              messages.value[assistantMessageIndex].thinking = null
              scrollToBottom()
            } else if (parsed.sources) {
              // 来源信息
              messages.value[assistantMessageIndex].sources = parsed.sources
              scrollToBottom()
            } else if (parsed.message === 'done' || Object.keys(parsed).length === 0) {
              // 完成
              messages.value[assistantMessageIndex].thinking = null
            }
          } catch (err) {
            console.error('Parse error:', err)
          }
        }
      }
    }
  } catch (err) {
    console.error('Q&A Error:', err)
    messages.value[assistantMessageIndex].content = `很抱歉，服务出现问题：${err.message || '未知错误'}。请稍后再试或联系人工客服。`
    messages.value[assistantMessageIndex].thinking = null
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const viewSource = (id) => {
  router.push(`/cases/${id}`)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style lang="scss" scoped>
.qa-page-modern {
  height: calc(100vh - 100px);
  margin: -24px;
  display: flex;
}

.chat-layout {
  width: 100%;
  height: 100%;
  background: white;
}

/* Main Chat Area */
.chat-main {
  display: flex;
  flex-direction: column;
  padding: 0;
  background: #f9fafb;
}

.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #f3f4f6;

  .header-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .ai-avatar {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
  }

  .ai-meta {
    h3 { font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 4px; }
    p { font-size: 13px; color: #6b7280; margin: 0; }
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Message Bubbles */
.message-wrapper {
  display: flex;

  &.user {
    justify-content: flex-end;
  }

  &.assistant {
    justify-content: flex-start;
  }
}

.message-bubble {
  display: flex;
  gap: 16px;
  max-width: 80%;

  .avatar-col {
    flex-shrink: 0;
  }

  .content-col {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.assistant-avatar {
  background: #ddd6fe;
  color: #7c3aed;
}

.user-avatar {
  background: #bfdbfe;
  color: #2563eb;
}

.bubble-content {
  padding: 16px 20px;
  border-radius: 16px;
  line-height: 1.6;
  font-size: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);

  .message-wrapper.user & {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-bottom-right-radius: 4px;
  }

  .message-wrapper.assistant & {
    background: white;
    color: #374151;
    border-top-left-radius: 4px;
  }
}

/* Thinking Indicator */
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8b5cf6;
  font-size: 13px;
  margin-top: 8px;

  .el-icon {
    font-size: 16px;
  }
}

/* Sources Panel */
.sources-panel {
  margin-top: 4px;
  padding: 12px;
  background: rgba(255,255,255,0.6);
  border-radius: 8px;
  border: 1px solid #e5e7eb;

  .sources-header {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .source-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .source-tag {
      cursor: pointer;
      transition: all 0.2s;
      background: white;

      &:hover {
        border-color: #8b5cf6;
        color: #8b5cf6;
      }
    }
  }
}

/* Input Area */
.input-container {
  padding: 24px;
  background: white;
  border-top: 1px solid #f3f4f6;
}

.input-wrapper {
  position: relative;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 8px;
  background: white;
  transition: all 0.3s;

  &:focus-within {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
  }

  .chat-input {
    :deep(.el-textarea__inner) {
      box-shadow: none;
      resize: none;
      border: none;
      padding: 12px;
    }
  }

  .input-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 12px 8px;

    .hint {
      font-size: 12px;
      color: #9ca3af;
    }

    .send-btn {
      width: 40px;
      height: 40px;
      font-size: 18px;
      background:linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
      border: none;

      &:hover {
        transform: scale(1.05);
      }
    }
  }
}

/* Sidebar */
.chat-sidebar {
  border-left: 1px solid #f3f4f6;
  background: white;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-card {
  border: none;
  background: #f9fafb;
  border-radius: 12px;

  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  :deep(.el-card__header) {
    padding: 16px;
    border-bottom: 1px solid rgba(0,0,0,0.03);
  }
}

.quick-tags {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .quick-tag {
    padding: 10px 14px;
    background: white;
    border-radius: 8px;
    font-size: 13px;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;

    &:hover {
      border-color: #ddd6fe;
      color: #7c3aed;
      background: #fdfcff;
      transform: translateX(4px);
    }
  }
}

.mini-stats {
  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px dashed #e5e7eb;

    &:last-child { border-bottom: none; }

    .label { font-size: 13px; color: #6b7280; }
    .value { font-weight: 600; color: #111827; }
    .value.high { color: #10b981; }
  }
}
</style>

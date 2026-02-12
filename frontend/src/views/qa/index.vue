<template>
  <div class="qa-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never" class="qa-card">
          <template #header>
            <span>智能问答</span>
          </template>

          <div class="chat-container" ref="chatContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message', msg.role]"
            >
              <div class="message-avatar">
                <el-avatar v-if="msg.role === 'assistant'" :size="36" icon="ChatDotRound" />
                <el-avatar v-else :size="36" icon="UserFilled" />
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <div class="message-sources" v-if="msg.sources && msg.sources.length">
                  <div class="sources-label">参考来源：</div>
                  <el-link
                    v-for="source in msg.sources"
                    :key="source.id"
                    type="primary"
                    @click="viewSource(source.id)"
                  >
                    {{ source.title }}
                  </el-link>
                </div>
              </div>
            </div>

            <div v-if="loading" class="message assistant">
              <div class="message-avatar">
                <el-avatar :size="36" icon="ChatDotRound" />
              </div>
              <div class="message-content">
                <div class="loading">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </div>
              </div>
            </div>
          </div>

          <div class="input-area">
            <el-input
              v-model="question"
              placeholder="请输入您的问题..."
              @keyup.enter="handleAsk"
              :disabled="loading"
            >
              <template #append>
                <el-button type="primary" @click="handleAsk" :loading="loading">
                  <el-icon><Position /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>快捷问题</span>
          </template>
          <div class="quick-questions">
            <el-button
              v-for="q in quickQuestions"
              :key="q"
              type="text"
              @click="question = q"
            >
              {{ q }}
            </el-button>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top: 20px">
          <template #header>
            <span>问答统计</span>
          </template>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-value">85%</span>
              <span class="stat-label">今日AI解决率</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">128</span>
              <span class="stat-label">今日问答数</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { qaApi } from '@/services/case'

const router = useRouter()
const chatContainer = ref(null)
const question = ref('')
const loading = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是 UniKnow 智能助手。请输入您的问题，我会尽力为您解答。'
  }
])

const quickQuestions = [
  '如何重置密码？',
  '如何查询账单？',
  '产品有哪些功能？',
  '如何联系客服？',
  '退款政策是什么？'
]

const formatMessage = (content) => {
  return content.replace(/\n/g, '<br>')
}

const handleAsk = async () => {
  if (!question.value.trim() || loading.value) return

  messages.value.push({
    role: 'user',
    content: question.value
  })

  const userQuestion = question.value
  question.value = ''
  loading.value = true

  try {
    const res = await qaApi.ask(userQuestion)
    const data = res.data || res

    messages.value.push({
      role: 'assistant',
      content: data.answer,
      sources: data.sources || []
    })
  } catch (e) {
    // 模拟回答
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我现在无法回答您的问题。您可以尝试重新提问，或者联系人工客服获取帮助。',
      sources: []
    })
  } finally {
    loading.value = false
    nextTick(() => {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    })
  }
}

const viewSource = (id) => {
  router.push(`/cases/${id}`)
}

onMounted(() => {
  nextTick(() => {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  })
})
</script>

<style lang="scss" scoped>
.qa-page {
  .qa-card {
    height: calc(100vh - 140px);
    display: flex;
    flex-direction: column;
  }

  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px 0;
  }

  .message {
    display: flex;
    margin-bottom: 20px;

    &.user {
      flex-direction: row-reverse;

      .message-content {
        background: $primary-color;
        color: #fff;

        .message-sources {
          display: none;
        }
      }
    }

    &.assistant {
      .message-content {
        background: #f4f4f5;
      }
    }
  }

  .message-avatar {
    flex-shrink: 0;
    margin: 0 12px;
  }

  .message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 8px;
    line-height: 1.6;
  }

  .message-sources {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(0, 0, 0, 0.1);

    .sources-label {
      font-size: 12px;
      color: $text-secondary;
      margin-bottom: 5px;
    }

    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .loading {
    display: flex;
    gap: 4px;

    .dot {
      width: 8px;
      height: 8px;
      background: $text-secondary;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;

      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
    }
  }

  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }

  .input-area {
    padding-top: 20px;
    border-top: 1px solid $border-light;
  }

  .quick-questions {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .el-button {
      justify-content: flex-start;
    }
  }

  .stats {
    display: flex;
    gap: 20px;

    .stat-item {
      text-align: center;

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: $primary-color;
        display: block;
      }

      .stat-label {
        font-size: 12px;
        color: $text-secondary;
      }
    }
  }
}
</style>

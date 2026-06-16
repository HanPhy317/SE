<template>
  <div v-if="open" class="chat-overlay" @click.self="$emit('close')">
    <section class="chat-panel" role="dialog" aria-modal="true" aria-label="订单聊天">
      <header class="chat-header">
        <div>
          <h3>订单聊天</h3>
          <p>{{ orderNo || room }}</p>
        </div>
        <button class="chat-icon-btn" type="button" title="关闭" @click="$emit('close')">×</button>
      </header>

      <div ref="messageBox" class="chat-messages">
        <div v-if="messages.length === 0" class="chat-empty">暂无消息</div>
        <article
          v-for="message in messages"
          :key="message.id"
          class="chat-message"
          :class="{ mine: message.sender === sender }"
        >
          <div class="chat-meta">{{ message.sender }} · {{ formatTime(message.created_at) }}</div>
          <div class="chat-bubble">{{ message.text }}</div>
        </article>
      </div>

      <form class="chat-form" @submit.prevent="send">
        <div class="emoji-wrap">
          <button class="emoji-toggle" type="button" title="表情" @click="emojiOpen = !emojiOpen">☺</button>
          <div v-if="emojiOpen" class="emoji-panel">
            <button
              v-for="emoji in emojis"
              :key="emoji"
              type="button"
              @click="addEmoji(emoji)"
            >
              {{ emoji }}
            </button>
          </div>
        </div>
        <input v-model.trim="draft" maxlength="1000" placeholder="输入消息" />
        <button type="submit" :disabled="!draft">发送</button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps({
  open: { type: Boolean, default: false },
  orderId: { type: [Number, String], required: true },
  orderNo: { type: String, default: '' },
})

defineEmits(['close'])

const userStore = useUserStore()
const messages = ref([])
const draft = ref('')
const emojiOpen = ref(false)
const messageBox = ref(null)
const socket = ref(null)
const seen = new Set()
const emojis = ['😀', '😂', '😊', '😍', '👍', '🙏', '👌', '🎉', '🚚', '📦', '🍱', '☕', '❤️', '🔥', '😅', '😭']

const room = computed(() => `order-${props.orderId}`)
const sender = computed(() => userStore.userInfo?.username || '用户')
const chatBase = `${window.location.protocol}//${window.location.hostname}:8001`
const cacheKey = computed(() => `chat-history:${room.value}`)

function scrollBottom() {
  nextTick(() => {
    if (messageBox.value) messageBox.value.scrollTop = messageBox.value.scrollHeight
  })
}

function appendMessage(message) {
  if (!message?.id || seen.has(message.id)) return
  seen.add(message.id)
  messages.value.push(message)
  saveLocalHistory()
  scrollBottom()
}

function saveLocalHistory() {
  localStorage.setItem(cacheKey.value, JSON.stringify(messages.value))
}

function loadLocalHistory() {
  try {
    const cached = JSON.parse(localStorage.getItem(cacheKey.value) || '[]')
    cached.forEach(appendMessage)
  } catch {
    localStorage.removeItem(cacheKey.value)
  }
}

function formatTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function loadHistory() {
  seen.clear()
  messages.value = []
  loadLocalHistory()

  try {
    const response = await fetch(`${chatBase}/api/chat/history/${encodeURIComponent(room.value)}`)
    if (!response.ok) return
    const history = await response.json()
    history.forEach(appendMessage)
  } catch {
    // Keep locally cached messages visible if the chat service is temporarily unavailable.
  }
}

async function connect() {
  closeSocket()
  await loadHistory()
  const wsBase = chatBase.replace(/^http/, 'ws')
  socket.value = new WebSocket(`${wsBase}/ws/chat/${encodeURIComponent(room.value)}`)
  socket.value.addEventListener('message', event => appendMessage(JSON.parse(event.data)))
}

function closeSocket() {
  if (socket.value) {
    socket.value.close()
    socket.value = null
  }
}

function addEmoji(emoji) {
  draft.value = `${draft.value}${emoji}`
}

async function send() {
  const text = draft.value
  if (!text) return

  const response = await fetch(`${chatBase}/api/chat/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room: room.value, sender: sender.value, text }),
  })

  if (response.ok) {
    appendMessage(await response.json())
    draft.value = ''
    emojiOpen.value = false
  }
}

watch(
  () => props.open,
  isOpen => {
    if (isOpen) connect()
    else closeSocket()
  },
  { immediate: true }
)

onBeforeUnmount(closeSocket)
</script>

<style scoped>
.chat-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(17, 24, 39, 0.42);
}

.chat-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  width: min(560px, 100%);
  height: min(680px, 86vh);
  overflow: hidden;
  background: #fff;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 -10px 35px rgba(15, 23, 42, 0.2);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header h3 {
  margin: 0;
  font-size: 17px;
}

.chat-header p {
  margin: 3px 0 0;
  color: #667085;
  font-size: 12px;
}

.chat-icon-btn {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 50%;
  background: #f2f4f7;
  color: #344054;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.chat-messages {
  overflow-y: auto;
  padding: 14px 16px;
  background: #f8fafc;
}

.chat-empty {
  color: #98a2b3;
  text-align: center;
  padding: 28px 0;
}

.chat-message {
  display: grid;
  justify-items: start;
  gap: 4px;
  margin-bottom: 12px;
}

.chat-message.mine {
  justify-items: end;
}

.chat-meta {
  color: #667085;
  font-size: 12px;
}

.chat-bubble {
  max-width: 82%;
  padding: 9px 11px;
  border-radius: 8px;
  background: #eef2f6;
  color: #1f2937;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.mine .chat-bubble {
  background: #e7f1ff;
}

.chat-form {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  padding: 12px 14px calc(12px + env(safe-area-inset-bottom));
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

.emoji-wrap {
  position: relative;
}

.emoji-toggle {
  width: 42px;
  min-height: 42px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #fff;
  color: #344054;
  font-size: 20px;
  cursor: pointer;
}

.emoji-panel {
  position: absolute;
  left: 0;
  bottom: 50px;
  display: grid;
  grid-template-columns: repeat(4, 38px);
  gap: 6px;
  padding: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.16);
}

.emoji-panel button {
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 20px;
  cursor: pointer;
}

.emoji-panel button:hover {
  background: #eef2f6;
}

.chat-form input {
  min-width: 0;
  min-height: 42px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  padding: 0 12px;
  font: inherit;
  outline: none;
}

.chat-form input:focus {
  border-color: #1677ff;
  box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.12);
}

.chat-form button[type="submit"] {
  min-height: 42px;
  border: 0;
  border-radius: 8px;
  padding: 0 18px;
  background: #1677ff;
  color: #fff;
  cursor: pointer;
}

.chat-form button[type="submit"]:disabled {
  background: #b2c8e8;
  cursor: not-allowed;
}

@media (min-width: 680px) {
  .chat-overlay {
    align-items: center;
  }

  .chat-panel {
    border-radius: 8px;
  }
}
</style>

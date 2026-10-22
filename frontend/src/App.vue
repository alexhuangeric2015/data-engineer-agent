<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const mode = ref('REACT')
const question = ref('')
const sessionId = ref('')
const messages = ref([])
const busy = ref(false)
const feed = ref(null)

// 模型输出可能包含 Markdown 表格；清理生成的 HTML 后再展示。
function renderMarkdown(content) {
  return DOMPurify.sanitize(marked.parse(content || ''))
}

// 新会话只重置界面状态，旧消息仍保存在服务端数据库。
function newChat() {
  if (busy.value) return
  sessionId.value = ''
  messages.value = []
}

// SSE 协议事件分别更新会话、计划、增量文本和错误提示。
function handleEvent(event, assistant) {
  if (event.sessionId) sessionId.value = event.sessionId
  if (event.type === 'plan') assistant.plan = event.text
  if (event.type === 'delta') assistant.content += event.text
  if (event.type === 'error') assistant.error = event.text || '请求失败'
}

// fetch 支持 POST 请求体；按空行切出 SSE 帧，保留跨网络块的未完数据。
async function submit() {
  const text = question.value.trim()
  if (!text || busy.value) return
  question.value = ''
  busy.value = true
  messages.value.push({ role: 'user', content: text })
  const assistant = { role: 'assistant', content: '', plan: '', error: '' }
  messages.value.push(assistant)
  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify({ sessionId: sessionId.value || null, question: text, mode: mode.value })
    })
    if (!response.ok || !response.body) throw new Error(`服务返回 ${response.status}`)
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer = (buffer + decoder.decode(value, { stream: true })).replaceAll('\r\n', '\n')
      let boundary
      while ((boundary = buffer.indexOf('\n\n')) >= 0) {
        const frame = buffer.slice(0, boundary)
        buffer = buffer.slice(boundary + 2)
        const data = frame.split('\n').filter(line => line.startsWith('data:')).map(line => line.slice(5).trimStart()).join('\n')
        if (data) handleEvent(JSON.parse(data), assistant)
        await nextTick()
        feed.value?.scrollTo({ top: feed.value.scrollHeight, behavior: 'smooth' })
      }
    }
  } catch (error) {
    assistant.error = error.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <main class="shell">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">◇</span><div><strong>数据资产助手</strong><small>HiAgent × Spring AI Alibaba</small></div></div>
      <button class="new-chat" type="button" @click="newChat">＋ 新建对话</button>
      <div class="sidebar-bottom"><span class="status-dot"></span> 本地 Demo <small>知识定位 · 数据核验 · 模型总结</small></div>
    </aside>
    <section class="workspace">
      <header class="topbar">
        <div><span class="eyebrow">DATA ASSET AGENT</span><h1>数据资产智能对话</h1></div>
        <div class="mode-switch" aria-label="执行模式">
          <button type="button" :class="{ active: mode === 'REACT' }" :disabled="busy" @click="mode = 'REACT'">ReAct</button>
          <button type="button" :class="{ active: mode === 'PLAN_AND_EXECUTE' }" :disabled="busy" @click="mode = 'PLAN_AND_EXECUTE'">Plan & Execute</button>
        </div>
      </header>
      <div ref="feed" class="feed" aria-live="polite">
        <div v-if="!messages.length" class="welcome">
          <div class="welcome-icon">✦</div><p class="eyebrow">ASK ABOUT YOUR DATA</p>
          <h2>从知识定位，到可信回答</h2>
          <p>询问表、字段、字典类型或码值。命中的知识片段只用于定位，实际结果由数据库核验。</p>
          <div class="examples">
            <button type="button" @click="question = '帮我查找用户表有哪些字段'">查找表字段 <span>↗</span></button>
            <button type="button" @click="question = '查询证件类型字典的全部码值'">查询字典码值 <span>↗</span></button>
          </div>
        </div>
        <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
          <div class="avatar">{{ message.role === 'user' ? '我' : '✦' }}</div>
          <div class="message-body"><div class="message-name">{{ message.role === 'user' ? '你' : '数据资产助手' }}</div>
            <details v-if="message.plan" class="plan"><summary>查看执行计划</summary><div>{{ message.plan }}</div></details>
            <div v-if="message.role === 'assistant'" class="content markdown" v-html="renderMarkdown(message.content || (busy && index === messages.length - 1 ? '正在检索与核验…' : ''))"></div>
            <div v-else class="content">{{ message.content }}</div>
            <div v-if="message.error" class="error">{{ message.error }}</div>
          </div>
        </div>
      </div>
      <form class="composer" @submit.prevent="submit">
        <label for="question">输入你的数据资产问题</label>
        <div class="input-wrap"><textarea id="question" v-model="question" rows="2" placeholder="例如：订单状态字段关联哪个字典？" :disabled="busy" @keydown.enter.exact.prevent="submit"></textarea>
          <button type="submit" :disabled="busy || !question.trim()" aria-label="发送问题">{{ busy ? '···' : '↑' }}</button></div>
        <p>Enter 发送 · Shift + Enter 换行 · 当前模式：{{ mode === 'REACT' ? 'ReAct' : 'Plan & Execute' }}</p>
      </form>
    </section>
  </main>
</template>

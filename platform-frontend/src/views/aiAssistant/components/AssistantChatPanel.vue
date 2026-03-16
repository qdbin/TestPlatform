<template>
  <div class="main-content">
    <div class="chat-header">
      <div class="header-left">
        <span class="title">AI 智能测试助手</span>
      </div>
      <div class="header-right">
        <el-switch :value="useRag" active-text="RAG" inactive-text="纯对话" @change="$emit('update:use-rag', $event)"></el-switch>
      </div>
    </div>

    <div class="message-area" ref="messageArea">
      <div v-if="!currentConversationId" class="welcome-tip">
        <i class="el-icon-thumb"></i>
        <h3>欢迎使用 AI 智能测试助手</h3>
        <p>我可以帮助你：</p>
        <ul>
          <li>回答关于 API 测试的问题</li>
          <li>解读接口文档和测试结果</li>
          <li>生成测试用例</li>
          <li>提供测试建议</li>
        </ul>
        <el-button type="primary" @click="$emit('create-chat')">开始对话</el-button>
      </div>

      <div v-else class="messages">
        <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.role">
          <div v-if="msg.role === 'user'" class="avatar">
            <i class="el-icon-user"></i>
          </div>
          <div class="content">
            <div v-if="msg.role === 'user'" class="bubble user-bubble">{{ msg.content }}</div>
            <div v-else>
              <div class="assistant-markdown" v-html="renderContent(msg.content || '')"></div>
              <div v-if="msg.caseData" class="ai-card case-card">
                <div class="card-header">
                  <i class="el-icon-s-order"></i> 用例预览已生成
                </div>
                <div class="card-body">
                  <p>已基于现有接口生成测试用例：<strong>{{ msg.caseData.name }}</strong></p>
                  <p v-if="Array.isArray(msg.apiIds) && msg.apiIds.length">关联接口ID：{{ msg.apiIds.join(", ") }}</p>
                  <div class="card-actions">
                    <el-button type="warning" size="small" @click="$emit('open-case-editor', msg)">打开用例新增页</el-button>
                  </div>
                </div>
              </div>
            </div>
            <div class="time">{{ formatTime(msg.time) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <el-input
        :value="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入问题，按 Enter 发送，Shift+Enter 换行"
        @input="$emit('update-input', $event)"
        @keydown.enter.native="$emit('enter', $event)"
        :disabled="isSending"
      ></el-input>
      <el-button type="primary" :disabled="!canSend" @click="$emit('send-action')">
        {{ isSending ? "停止" : "发送" }}
      </el-button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "AssistantChatPanel",
  emits: [
    "update:use-rag",
    "update-input",
    "create-chat",
    "enter",
    "send-action",
    "open-case-editor",
  ],
  props: {
    useRag: { type: Boolean, default: true },
    currentConversationId: { type: String, default: "" },
    messages: { type: Array, default: () => [] },
    inputMessage: { type: String, default: "" },
    canSend: { type: Boolean, default: false },
    isSending: { type: Boolean, default: false },
    renderContent: { type: Function, required: true },
    formatTime: { type: Function, required: true },
  },
});
</script>

<style scoped>
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #f3f6fb;
}

.chat-header {
  height: 58px;
  padding: 0 20px;
  border-bottom: 1px solid #e8eef7;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left .title {
  font-size: 16px;
  font-weight: 700;
  color: #2f3442;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px;
}

.welcome-tip {
  max-width: 760px;
  margin: 34px auto;
  background: #fff;
  border: 1px solid #e7edf5;
  border-radius: 16px;
  text-align: center;
  padding: 42px 30px;
  color: #6a7383;
  box-shadow: 0 10px 25px rgba(27, 39, 94, 0.06);
}

.welcome-tip i {
  font-size: 48px;
  color: #4d8eff;
}

.welcome-tip h3 {
  color: #2f3442;
  margin: 10px 0 14px;
}

.welcome-tip ul {
  text-align: left;
  display: inline-block;
  margin: 12px 0 18px;
  line-height: 1.8;
}

.messages {
  width: 100%;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 18px;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 10px;
  color: #fff;
  background: linear-gradient(135deg, #54a5ff 0%, #3479ef 100%);
}

.content {
  max-width: min(100%, 1200px);
  width: fit-content;
}

.bubble {
  display: inline-block;
  padding: 11px 14px;
  border-radius: 12px;
  line-height: 1.65;
  word-break: break-word;
}

.user-bubble {
  color: #fff;
  background: linear-gradient(135deg, #4c8dff 0%, #3a77e6 100%);
  box-shadow: 0 8px 20px rgba(69, 126, 233, 0.24);
}

.message.assistant .content {
  max-width: min(100%, 1200px);
  width: 100%;
  padding: 2px 0 0;
}

.assistant-markdown {
  color: #2f3442;
  line-height: 1.7;
}

.assistant-markdown :deep(h1),
.assistant-markdown :deep(h2),
.assistant-markdown :deep(h3),
.assistant-markdown :deep(h4) {
  margin: 10px 0 6px;
  line-height: 1.4;
}

.assistant-markdown :deep(p) {
  margin: 0 0 8px;
}

.assistant-markdown :deep(pre) {
  margin: 8px 0;
  border-radius: 8px;
  padding: 10px;
  white-space: pre-wrap;
  background: #f6f8fc;
}

.assistant-markdown :deep(code) {
  font-family: Consolas, "Courier New", monospace;
}

.assistant-markdown :deep(ul),
.assistant-markdown :deep(ol) {
  margin: 6px 0 10px;
  padding-left: 18px;
}

.assistant-markdown :deep(.mermaid) {
  overflow-x: auto;
}

.ai-card {
  margin-top: 10px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e9edf5;
  background: #fbfdff;
}

.card-header {
  padding: 8px 10px;
  background: #f3f7ff;
  color: #3f6fca;
  font-weight: 600;
}

.card-body {
  padding: 10px;
  color: #5d6676;
}

.card-body p {
  margin: 0 0 8px;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
}

.time {
  margin-top: 6px;
  font-size: 12px;
  color: #97a0af;
}

.message.user .time {
  text-align: right;
}

.input-area {
  background: #fff;
  border-top: 1px solid #e8eef7;
  padding: 14px 20px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-area :deep(.el-textarea) {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 10px;
  border-color: #dce5f3;
  min-height: 44px !important;
}

.assistant-markdown :deep(.hljs) {
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid #e7edf5;
  background: #0f172a;
  color: #e2e8f0;
}

.input-area .el-button {
  height: 40px;
  min-width: 88px;
  border-radius: 10px;
  font-weight: 600;
}
</style>

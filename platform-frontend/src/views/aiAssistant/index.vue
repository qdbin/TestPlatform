/**
 * AI助手页面
 */
<template>
  <div class="ai-assistant">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <el-button
          type="primary"
          icon="el-icon-plus"
          size="small"
          @click="createNewChat"
          :disabled="historyReadOnly"
          >新建对话</el-button
        >
      </div>

      <el-tabs v-model="activeTab" class="sidebar-tabs">
        <el-tab-pane label="会话" name="chat">
          <div class="conversation-list">
            <div
              v-for="conv in conversationList"
              :key="conv.id"
              class="conversation-item"
              :class="{ active: currentConversationId === conv.id }"
              @click="selectConversation(conv)"
            >
              <i class="el-icon-chat-line-round"></i>
              <span class="conv-title">{{ conv.title || "新会话" }}</span>
              <el-dropdown
                trigger="click"
                @command="handleConvCommand($event, conv)"
              >
                <i class="el-icon-more"></i>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item command="delete">删除</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
            <div v-if="conversationList.length === 0" class="empty-tip">
              暂无会话记录
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="知识库" name="knowledge">
          <div class="knowledge-list">
            <el-button
              size="small"
              icon="el-icon-plus"
              @click="showKnowledgeDialog = true"
              >添加文档</el-button
            >
            <div class="knowledge-items">
              <div
                v-for="kb in knowledgeList"
                :key="kb.id"
                class="knowledge-item"
              >
                <i class="el-icon-document"></i>
                <span>{{ kb.name }}</span>
                <el-tag
                  size="mini"
                  :type="kb.indexedStatus === 'ready' ? 'success' : 'warning'"
                >
                  {{ kb.indexedStatus === "ready" ? "已索引" : "待索引" }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="sidebar-footer">
        <el-button size="small" @click="exportLocalHistory">
          <i class="el-icon-download"></i> 导出
        </el-button>
        <el-button size="small" type="warning" @click="resetLocalHistory">
          <i class="el-icon-refresh"></i> 重置
        </el-button>
        <el-button size="small" type="danger" @click="clearLocalHistory">
          <i class="el-icon-delete"></i> 清空
        </el-button>
        <div v-if="historyReadOnly" class="storage-limit-tip">
          <el-tag type="danger" size="mini">本地存储已满（只读）</el-tag>
        </div>
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="main-content">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <span class="title">AI 智能测试助手</span>
        </div>
        <div class="header-right">
          <el-switch v-model="useRag" active-text="RAG" inactive-text="纯对话">
          </el-switch>
        </div>
      </div>

      <!-- 消息区域 -->
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
          <el-button type="primary" @click="createNewChat">开始对话</el-button>
        </div>

        <div v-else class="messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
            :class="msg.role"
          >
            <div class="avatar">
              <i
                :class="msg.role === 'user' ? 'el-icon-user' : 'el-icon-cpu'"
              ></i>
            </div>
            <div class="content">
              <div class="bubble" v-html="renderContent(msg.content)"></div>
              <div class="time">{{ formatTime(msg.time) }}</div>
            </div>
          </div>

          <div v-if="isLoading" class="message assistant loading">
            <div class="avatar">
              <i class="el-icon-cpu"></i>
            </div>
            <div class="content">
              <div class="bubble">
                <span class="loading-dots">
                  <span></span><span></span><span></span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="请输入问题，按 Enter 发送，Shift+Enter 换行"
          @keydown.enter.native="handleEnter"
          :disabled="isLoading || historyReadOnly"
        >
        </el-input>
        <el-button
          type="primary"
          :loading="isLoading"
          :disabled="!inputMessage.trim() || historyReadOnly"
          @click="sendMessage"
        >
          发送
        </el-button>
      </div>
    </div>

    <!-- 用例生成对话框 -->
    <el-dialog
      title="AI 用例生成"
      :visible.sync="showCaseGenerate"
      width="800px"
    >
      <el-steps :active="caseGenerateStep" finish-status="success">
        <el-step title="输入需求"></el-step>
        <el-step title="选择接口"></el-step>
        <el-step title="生成用例"></el-step>
        <el-step title="确认保存"></el-step>
      </el-steps>

      <div class="case-generate-content">
        <!-- 步骤1：输入需求 -->
        <div v-if="caseGenerateStep === 0">
          <el-input
            v-model="caseRequirement"
            type="textarea"
            :rows="4"
            placeholder="请描述你的测试需求，如：测试用户登录接口"
          ></el-input>
          <el-button type="primary" @click="nextCaseStep">下一步</el-button>
        </div>

        <!-- 步骤2：选择接口 -->
        <div v-if="caseGenerateStep === 1">
          <el-checkbox-group v-model="selectedApis">
            <el-checkbox v-for="api in apiList" :key="api.id" :label="api.id">
              {{ api.name }} - {{ api.method }} {{ api.path }}
            </el-checkbox>
          </el-checkbox-group>
          <el-button @click="caseGenerateStep = 0">上一步</el-button>
          <el-button type="primary" @click="generateCase">生成用例</el-button>
        </div>

        <!-- 步骤3：生成用例 -->
        <div v-if="caseGenerateStep === 2">
          <pre class="case-preview">{{ generatedCase }}</pre>
          <el-button @click="caseGenerateStep = 1">上一步</el-button>
          <el-button type="primary" @click="saveGeneratedCase"
            >确认并保存</el-button
          >
        </div>
      </div>
    </el-dialog>

    <!-- 知识库添加对话框 -->
    <el-dialog
      title="添加知识库文档"
      :visible.sync="showKnowledgeDialog"
      width="600px"
    >
      <el-form :model="knowledgeForm" label-width="80px">
        <el-form-item label="文档名称">
          <el-input
            v-model="knowledgeForm.name"
            placeholder="请输入文档名称"
          ></el-input>
        </el-form-item>
        <el-form-item label="文档类型">
          <el-select v-model="knowledgeForm.docType" placeholder="请选择">
            <el-option label="使用手册" value="manual"></el-option>
            <el-option label="引导文档" value="guide"></el-option>
            <el-option label="接口文档" value="api_doc"></el-option>
            <el-option label="自定义" value="custom"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文档内容">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文档内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showKnowledgeDialog = false">取消</el-button>
        <el-button type="primary" @click="saveKnowledge">保存并索引</el-button>
      </div>
    </el-dialog>

    <!-- 本地存储容量提示 -->
    <el-dialog title="本地存储容量提示" :visible.sync="showStorageLimitDialog" width="520px">
      <div>
        当前 AI 历史对话仅保存在浏览器本地（localStorage）。
        <br />
        你当前存储已达到或超过 5MB，为避免浏览器写入失败，已自动进入只读模式。
        <br />
        你可以先导出备份，再重置或清空历史。
      </div>
      <div slot="footer">
        <el-button @click="exportLocalHistory">导出</el-button>
        <el-button type="warning" @click="resetLocalHistory">重置</el-button>
        <el-button type="primary" @click="showStorageLimitDialog = false">我知道了</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: "AIAssistant",
  data() {
    return {
      // 侧边栏
      activeTab: "chat",
      conversationList: [],
      knowledgeList: [],
      currentConversationId: null,
      historyReadOnly: false,
      showStorageLimitDialog: false,

      // 聊天
      inputMessage: "",
      messages: [],
      isLoading: false,
      useRag: true,

      // 用例生成
      showCaseGenerate: false,
      caseGenerateStep: 0,
      caseRequirement: "",
      apiList: [],
      selectedApis: [],
      generatedCase: "",

      // 知识库
      showKnowledgeDialog: false,
      knowledgeForm: {
        name: "",
        docType: "manual",
        content: "",
      },
    };
  },
  mounted() {
    this.loadConversations();
    this.loadKnowledgeList();
  },
  methods: {
    getResponseData(res) {
      if (!res || !res.data) return null;
      if (Object.prototype.hasOwnProperty.call(res.data, "data"))
        return res.data.data;
      return res.data;
    },

    getHistoryStorageKey() {
      const projectId =
        this.$store.state.project?.id || localStorage.getItem("projectId") || "";
      const userId =
        this.$store.state.user?.id || localStorage.getItem("userId") || "";
      return `ai_chat_history_v1:${projectId}:${userId}`;
    },

    estimateSizeBytes(text) {
      try {
        return new Blob([text]).size;
      } catch (e) {
        return (text || "").length;
      }
    },

    tryPersistHistory(conversationList) {
      const key = this.getHistoryStorageKey();
      const json = JSON.stringify(conversationList || []);
      const size = this.estimateSizeBytes(json);
      if (size >= 5 * 1024 * 1024) {
        this.historyReadOnly = true;
        this.showStorageLimitDialog = true;
        return false;
      }

      try {
        localStorage.setItem(key, json);
        return true;
      } catch (e) {
        this.historyReadOnly = true;
        this.showStorageLimitDialog = true;
        return false;
      }
    },

    loadConversations() {
      const key = this.getHistoryStorageKey();
      const raw = localStorage.getItem(key);
      if (!raw) {
        this.conversationList = [];
        this.historyReadOnly = false;
        return;
      }
      const size = this.estimateSizeBytes(raw);
      if (size >= 5 * 1024 * 1024) {
        this.historyReadOnly = true;
        this.showStorageLimitDialog = true;
      } else {
        this.historyReadOnly = false;
      }

      try {
        const list = JSON.parse(raw);
        this.conversationList = Array.isArray(list) ? list : [];
      } catch (e) {
        this.conversationList = [];
      }
    },

    // 创建新会话（仅本地存储）
    createNewChat() {
      if (this.historyReadOnly) return;
      const id = `${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const conv = {
        id,
        title: "新会话",
        messages: [],
        createTime: Date.now(),
        updateTime: Date.now(),
      };
      const next = [conv, ...this.conversationList];
      if (!this.tryPersistHistory(next)) return;
      this.conversationList = next;
      this.currentConversationId = id;
      this.messages = [];
    },

    // 选择会话（仅本地存储）
    selectConversation(conv) {
      this.currentConversationId = conv.id;
      this.messages = Array.isArray(conv.messages) ? conv.messages : [];
      this.scrollToBottom();
    },

    // 处理会话操作（仅本地存储）
    handleConvCommand(command, conv) {
      if (this.historyReadOnly) return;
      if (command === "delete") {
        const next = this.conversationList.filter((c) => c.id !== conv.id);
        if (!this.tryPersistHistory(next)) return;
        this.conversationList = next;
        if (this.currentConversationId === conv.id) {
          this.currentConversationId = null;
          this.messages = [];
        }
      }
    },

    updateCurrentConversationMessages(messages) {
      const id = this.currentConversationId;
      if (!id) return;
      const next = this.conversationList.map((c) => {
        if (c.id !== id) return c;
        const title = c.title && c.title !== "新会话" ? c.title : (messages[0]?.content || "新会话").slice(0, 20);
        return {
          ...c,
          title,
          messages,
          updateTime: Date.now(),
        };
      });
      if (!this.tryPersistHistory(next)) return;
      this.conversationList = next;
    },

    // 发送消息
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return;
      if (this.historyReadOnly) return;

      const projectId =
        this.$store.state.project?.id || localStorage.getItem("projectId");
      const userId =
        this.$store.state.user?.id || localStorage.getItem("userId");

      if (!this.currentConversationId) {
        this.createNewChat();
      }

      // 添加用户消息
      const userMsg = {
        role: "user",
        content: this.inputMessage,
        time: Date.now(),
      };
      this.messages.push(userMsg);
      this.updateCurrentConversationMessages(this.messages);

      const inputMsg = this.inputMessage;
      this.inputMessage = "";
      this.isLoading = true;
      this.scrollToBottom();

      try {
        // 使用SSE流式接收
        const response = await fetch(
          `${this.$axios.defaults.baseURL}/autotest/ai/chat/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              token: localStorage.getItem("token"),
            },
            body: JSON.stringify({
              projectId: projectId,
              userId: userId,
              message: inputMsg,
              useRag: this.useRag,
              conversationId: this.currentConversationId,
            }),
          }
        );

        if (!response.ok || !response.body) {
          throw new Error(`网络异常或服务错误（HTTP ${response.status}）`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let assistantMsg = {
          role: "assistant",
          content: "",
          time: Date.now(),
        };

        this.messages.push(assistantMsg);
        this.scrollToBottom();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split("\n");

          for (const line of lines) {
            if (line.startsWith("data:")) {
              try {
                const payload = line.replace(/^data:\s*/, "");
                const data = JSON.parse(payload);
                if (data.type === "content" && data.delta) {
                  assistantMsg.content += data.delta;
                  this.scrollToBottom();
                } else if (data.type === "case" && data.case) {
                  this.generatedCase = JSON.stringify(data.case, null, 2);
                  this.caseGenerateStep = 2;
                  this.showCaseGenerate = true;
                } else if (data.type === "end") {
                  break;
                } else if (data.type === "error") {
                  throw new Error(data.message || "AI服务错误");
                }
              } catch (e) {
                // 忽略解析错误
              }
            }
          }
        }
        this.updateCurrentConversationMessages(this.messages);
      } catch (error) {
        this.messages.push({
          role: "assistant",
          content: `AI服务调用失败：${error.message}`,
          time: Date.now(),
        });
        this.updateCurrentConversationMessages(this.messages);
        this.$message.error("AI服务调用失败：" + error.message);
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },

    exportLocalHistory() {
      const key = this.getHistoryStorageKey();
      const raw = localStorage.getItem(key) || "[]";
      const blob = new Blob([raw], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ai_history_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    },

    resetLocalHistory() {
      const key = this.getHistoryStorageKey();
      localStorage.removeItem(key);
      this.conversationList = [];
      this.currentConversationId = null;
      this.messages = [];
      this.historyReadOnly = false;
      this.showStorageLimitDialog = false;
      this.$message.success("已重置本地历史对话");
    },

    clearLocalHistory() {
      if (this.historyReadOnly) {
        this.$message.warning("当前为只读模式，请先重置或导出后再操作");
        return;
      }
      const next = [];
      if (!this.tryPersistHistory(next)) return;
      this.conversationList = [];
      this.currentConversationId = null;
      this.messages = [];
      this.$message.success("已清空本地历史对话");
    },

    // 回车发送
    handleEnter(e) {
      if (!e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    },

    // 滚动到底部
    scrollToBottom() {
      this.$nextTick(() => {
        const area = this.$refs.messageArea;
        if (area) {
          area.scrollTop = area.scrollHeight;
        }
      });
    },

    // 渲染内容（简单支持换行）
    renderContent(content) {
      if (!content) return "";
      return content.replace(/\n/g, "<br>");
    },

    // 格式化时间
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return `${date.getHours().toString().padStart(2, "0")}:${date
        .getMinutes()
        .toString()
        .padStart(2, "0")}`;
    },

    // 加载知识库列表
    async loadKnowledgeList() {
      const projectId =
        this.$store.state.project?.id || localStorage.getItem("projectId");
      const res = await this.$get(
        `/autotest/ai/knowledge?projectId=${projectId}`
      );
      const data = this.getResponseData(res);
      if (data) {
        this.knowledgeList = data;
      }
    },

    // 保存知识库
    async saveKnowledge() {
      const projectId =
        this.$store.state.project?.id || localStorage.getItem("projectId");
      const userId =
        this.$store.state.user?.id || localStorage.getItem("userId");

      const saveRes = await this.$post("/autotest/ai/knowledge", {
        projectId: projectId,
        name: this.knowledgeForm.name,
        docType: this.knowledgeForm.docType,
        content: this.knowledgeForm.content,
        sourceType: "manual",
        updateUser: userId,
      });

      const knowledgeId = this.getResponseData(saveRes);

      if (knowledgeId) {
        try {
          await this.$post(
            `/autotest/ai/knowledge/index/${knowledgeId}?projectId=${projectId}`
          );
          this.$message.success("保存成功，索引已提交");
        } catch (e) {
          this.$message.warning("保存成功，但索引提交失败");
        }
      } else {
        this.$message.success("保存成功");
      }
      this.showKnowledgeDialog = false;
      this.knowledgeForm = { name: "", docType: "manual", content: "" };
      this.loadKnowledgeList();
    },

    // 用例生成步骤
    async nextCaseStep() {
      if (this.caseGenerateStep === 0) {
        // 获取接口列表
        const projectId =
          this.$store.state.project?.id || localStorage.getItem("projectId");
        const res = await this.$get(`/autotest/ai/agent/api-list/${projectId}`);
        const data = this.getResponseData(res);
        if (data && data.data) {
          this.apiList = data.data;
        }
        this.caseGenerateStep = 1;
      }
    },

    // 生成用例
    async generateCase() {
      const projectId =
        this.$store.state.project?.id || localStorage.getItem("projectId");

      this.$message.info("正在生成用例，请稍候...");

      const res = await this.$post("/autotest/ai/generate/case", {
        projectId: projectId,
        userRequirement: this.caseRequirement,
        selectedApis: this.selectedApis,
      });

      const data = this.getResponseData(res);
      if (data && data.case) {
        this.generatedCase = JSON.stringify(data.case, null, 2);
        this.caseGenerateStep = 2;
      } else {
        this.$message.error("用例生成失败");
      }
    },

    // 保存用例
    async saveGeneratedCase() {
      // TODO: 调用后端保存用例接口
      this.$message.success("用例保存成功");
      this.showCaseGenerate = false;
      this.caseGenerateStep = 0;
      this.caseRequirement = "";
      this.selectedApis = [];
      this.generatedCase = "";
    },

  },
};
</script>

<style scoped>
.ai-assistant {
  display: flex;
  height: calc(100vh - 84px);
  background: #fff;
}

.sidebar {
  width: 280px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-tabs {
  flex: 1;
  overflow: hidden;
}

.sidebar-tabs >>> .el-tabs__content {
  height: calc(100% - 55px);
  overflow-y: auto;
}

.conversation-list,
.knowledge-list {
  padding: 10px;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.conversation-item:hover {
  background: #e4e7ed;
}

.conversation-item.active {
  background: #409eff;
  color: #fff;
}

.conv-title {
  flex: 1;
  margin-left: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.knowledge-item span {
  flex: 1;
  margin: 0 10px;
}

.sidebar-footer {
  padding: 10px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.storage-limit-tip {
  width: 100%;
  margin-top: 6px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  height: 50px;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-right .el-switch {
  margin-right: 20px;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafafa;
}

.welcome-tip {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.welcome-tip i {
  font-size: 60px;
  color: #409eff;
  margin-bottom: 20px;
}

.welcome-tip h3 {
  margin-bottom: 15px;
  color: #303133;
}

.welcome-tip ul {
  text-align: left;
  display: inline-block;
  margin: 20px 0;
}

.welcome-tip li {
  margin: 8px 0;
}

.messages {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message.user .avatar {
  background: #409eff;
  color: #fff;
}

.message.assistant .avatar {
  background: #67c23a;
  color: #fff;
}

.message .content {
  max-width: 70%;
  margin: 0 10px;
}

.message.user .content {
  text-align: right;
}

.message .bubble {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
  word-break: break-word;
}

.message.user .bubble {
  background: #409eff;
  color: #fff;
}

.message.assistant .bubble {
  background: #fff;
  border: 1px solid #e4e7ed;
}

.message .time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.loading-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin: 0 3px;
  background: #67c23a;
  border-radius: 50%;
  animation: loading 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}
.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 15px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
}

.input-area .el-textarea {
  flex: 1;
}

.case-generate-content {
  padding: 20px;
}

.case-preview {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 12px;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>

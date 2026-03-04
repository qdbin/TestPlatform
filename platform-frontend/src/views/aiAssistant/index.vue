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
          <div class="knowledge-entry">
            <el-button type="primary" size="small" @click="openKnowledgeManage">
              打开知识库管理
            </el-button>
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
              <div
                class="bubble"
                v-html="
                  renderContent(
                    msg.content ||
                      (msg.role === 'assistant' &&
                      currentConversationLoading &&
                      index === messages.length - 1
                        ? '思考中...'
                        : '')
                  )
                "
              ></div>
              <div class="time">{{ formatTime(msg.time) }}</div>
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
        >
        </el-input>
        <el-button
          type="primary"
          :disabled="!inputMessage.trim() && !currentConversationLoading"
          @click="handleSendAction"
        >
          {{ currentConversationLoading ? "停止" : "发送" }}
        </el-button>
      </div>
    </div>

    <!-- 知识库管理对话框 -->
    <el-dialog
      title="知识库管理"
      :visible.sync="showKnowledgeManageDialog"
      width="980px"
      append-to-body
      destroy-on-close
    >
      <div class="knowledge-manage">
        <div class="knowledge-toolbar">
          <el-button size="small" icon="el-icon-folder-add" @click="openCreateFolderDialog">
            新建目录
          </el-button>
          <el-button size="small" icon="el-icon-plus" type="primary" @click="openCreateKnowledgeDialog">
            添加文档
          </el-button>
        </div>
        <el-tree
          v-if="knowledgeTreeData.length > 0"
          :data="knowledgeTreeData"
          node-key="id"
          default-expand-all
          :expand-on-click-node="false"
          @node-click="handleKnowledgeNodeClick"
        >
          <span slot-scope="{ data }" class="knowledge-node">
            <span class="knowledge-node-main">
              <i :class="data.docType === 'folder' ? 'el-icon-folder' : 'el-icon-document'"></i>
              <span class="knowledge-node-title">{{ data.name || "未命名文档" }}</span>
              <el-tag
                v-if="data.docType !== 'folder'"
                size="mini"
                :type="knowledgeStatusType(data.indexedStatus)"
              >
                {{ knowledgeStatusText(data.indexedStatus) }}
              </el-tag>
            </span>
            <span class="knowledge-node-actions">
              <el-button
                v-if="data.docType === 'folder' && data.canEdit"
                type="text"
                size="mini"
                @click.stop="openCreateFolderDialog(data)"
              >
                新建子目录
              </el-button>
              <el-button
                v-if="data.docType === 'folder' && data.canEdit"
                type="text"
                size="mini"
                @click.stop="openCreateKnowledgeDialog(data)"
              >
                新建文档
              </el-button>
              <el-button
                v-if="data.docType !== 'folder'"
                type="text"
                size="mini"
                @click.stop="openViewKnowledge(data)"
              >
                查看
              </el-button>
              <el-button
                v-if="data.docType !== 'folder' && data.canEdit"
                type="text"
                size="mini"
                @click.stop="openEditKnowledge(data)"
              >
                编辑
              </el-button>
              <el-button
                v-if="data.docType !== 'folder' && data.canEdit"
                type="text"
                size="mini"
                @click.stop="reindexKnowledge(data)"
              >
                重建索引
              </el-button>
              <el-button
                v-if="data.canEdit"
                type="text"
                size="mini"
                style="color: #f56c6c"
                @click.stop="deleteKnowledge(data)"
              >
                删除
              </el-button>
            </span>
          </span>
        </el-tree>
        <div v-else class="empty-tip">暂无知识文档</div>
      </div>
    </el-dialog>

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
      :title="knowledgeDialogTitle"
      :visible.sync="showKnowledgeDialog"
      width="600px"
      @close="closeKnowledgeDialog"
    >
      <el-form :model="knowledgeForm" label-width="80px">
        <el-form-item label="文档名称">
          <el-input
            v-model="knowledgeForm.name"
            :disabled="isKnowledgeReadonly"
            placeholder="请输入文档名称"
          ></el-input>
        </el-form-item>
        <el-form-item label="文档类型">
          <el-select
            v-model="knowledgeForm.docType"
            :disabled="isKnowledgeReadonly"
            placeholder="请选择"
          >
            <el-option label="使用手册" value="manual"></el-option>
            <el-option label="引导文档" value="guide"></el-option>
            <el-option label="接口文档" value="api_doc"></el-option>
            <el-option label="自定义" value="custom"></el-option>
            <el-option label="目录" value="folder"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文档内容" v-if="knowledgeForm.docType !== 'folder'">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="10"
            :disabled="isKnowledgeReadonly"
            placeholder="请输入文档内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showKnowledgeDialog = false">取消</el-button>
        <el-button v-if="!isKnowledgeReadonly" type="primary" @click="saveKnowledge">
          {{ knowledgeForm.docType === "folder" ? "保存目录" : "保存并索引" }}
        </el-button>
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
import MarkdownIt from "markdown-it";
import mermaid from "mermaid";

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
      useRag: true,
      loadingMap: {},
      activeControllers: {},

      // 用例生成
      showCaseGenerate: false,
      caseGenerateStep: 0,
      caseRequirement: "",
      apiList: [],
      selectedApis: [],
      generatedCase: "",

      // 知识库
      showKnowledgeDialog: false,
      showKnowledgeManageDialog: false,
      selectedKnowledgeFolderId: "0",
      knowledgeTreeData: [],
      knowledgeDialogMode: "create",
      knowledgeForm: {
        id: "",
        parentId: "0",
        name: "",
        docType: "manual",
        content: "",
      },
      markdownIt: null,
      mermaidRenderTimer: null,
    };
  },
  computed: {
    currentConversationLoading() {
      if (!this.currentConversationId) return false;
      return (
        !!this.loadingMap[this.currentConversationId] &&
        !!this.activeControllers[this.currentConversationId]
      );
    },
    isKnowledgeReadonly() {
      return this.knowledgeDialogMode === "view";
    },
    knowledgeDialogTitle() {
      if (this.knowledgeDialogMode === "view") return "知识文档详情";
      if (this.knowledgeDialogMode === "edit") return "编辑知识文档";
      return "添加知识库文档";
    },
  },
  mounted() {
    this.initMarkdown();
    this.initMermaid();
    this.loadConversations();
    this.loadKnowledgeList();
    this.scheduleMermaidRender();
  },
  beforeDestroy() {
    Object.keys(this.activeControllers).forEach((id) => {
      const controller = this.activeControllers[id];
      if (controller && typeof controller.abort === "function") {
        controller.abort();
      }
    });
    if (this.mermaidRenderTimer) {
      clearTimeout(this.mermaidRenderTimer);
      this.mermaidRenderTimer = null;
    }
  },
  methods: {
    openKnowledgeManage() {
      this.showKnowledgeManageDialog = true;
      this.loadKnowledgeList();
    },
    getCurrentProjectId() {
      if (this.$store.state.projectId) return String(this.$store.state.projectId);
      if (this.$store.state.userInfo && this.$store.state.userInfo.lastProject) {
        const lastProject = this.$store.state.userInfo.lastProject;
        if (typeof lastProject === "string" || typeof lastProject === "number") {
          return String(lastProject);
        }
        if (typeof lastProject === "object" && lastProject.id) {
          return String(lastProject.id);
        }
      }
      const rawUser = localStorage.getItem("userInfo");
      if (rawUser) {
        try {
          const user = JSON.parse(rawUser);
          if (user && user.lastProject) {
            if (typeof user.lastProject === "string" || typeof user.lastProject === "number") {
              return String(user.lastProject);
            }
            if (typeof user.lastProject === "object" && user.lastProject.id) {
              return String(user.lastProject.id);
            }
          }
        } catch (e) {}
      }
      const projectId = localStorage.getItem("projectId");
      return projectId ? String(projectId) : "";
    },

    getCurrentUserId() {
      if (this.$store.state.userInfo && this.$store.state.userInfo.id) {
        return String(this.$store.state.userInfo.id);
      }
      const rawUser = localStorage.getItem("userInfo");
      if (rawUser) {
        try {
          const user = JSON.parse(rawUser);
          if (user && user.id) {
            return String(user.id);
          }
        } catch (e) {}
      }
      const userId = localStorage.getItem("userId");
      return userId ? String(userId) : "";
    },

    buildApiUrl(path) {
      const base = (this.$axios && this.$axios.defaults && this.$axios.defaults.baseURL) || "";
      if (!base || base === "/") {
        return path;
      }
      const normalizedBase = base.endsWith("/") ? base.slice(0, -1) : base;
      const normalizedPath = path.startsWith("/") ? path : `/${path}`;
      return `${normalizedBase}${normalizedPath}`;
    },

    getResponseData(res) {
      if (!res || !res.data) return null;
      let current = res.data;
      if (Object.prototype.hasOwnProperty.call(current, "data")) {
        current = current.data;
      }
      while (
        current &&
        typeof current === "object" &&
        !Array.isArray(current) &&
        Object.keys(current).length === 1 &&
        Object.prototype.hasOwnProperty.call(current, "data")
      ) {
        current = current.data;
      }
      return current;
    },

    getHistoryStorageKey() {
      const projectId = this.getCurrentProjectId();
      const userId = this.getCurrentUserId();
      if (projectId && userId) {
        return `ai_chat_history_v1:${projectId}:${userId}`;
      }
      const token = localStorage.getItem("token") || "anonymous";
      const tokenTail = token.slice(-12);
      return `ai_chat_history_v1:${projectId || "no_project"}:${userId || tokenTail}`;
    },

    estimateSizeBytes(text) {
      try {
        return new Blob([text]).size;
      } catch (e) {
        return (text || "").length;
      }
    },

    shrinkHistory(conversationList) {
      const list = Array.isArray(conversationList) ? [...conversationList] : [];
      let json = JSON.stringify(list);
      let size = this.estimateSizeBytes(json);
      while (size >= 4.5 * 1024 * 1024 && list.length > 1) {
        list.pop();
        json = JSON.stringify(list);
        size = this.estimateSizeBytes(json);
      }
      if (size >= 4.5 * 1024 * 1024 && list.length === 1) {
        const one = list[0];
        const msgs = Array.isArray(one.messages) ? [...one.messages] : [];
        while (msgs.length > 2 && size >= 4.5 * 1024 * 1024) {
          msgs.shift();
          one.messages = msgs;
          json = JSON.stringify(list);
          size = this.estimateSizeBytes(json);
        }
      }
      return list;
    },

    tryPersistHistory(conversationList) {
      const key = this.getHistoryStorageKey();
      let targetList = conversationList || [];
      let json = JSON.stringify(targetList);
      const size = this.estimateSizeBytes(json);
      if (size >= 5 * 1024 * 1024) {
        targetList = this.shrinkHistory(targetList);
        json = JSON.stringify(targetList);
      }

      try {
        localStorage.setItem(key, json);
        this.historyReadOnly = false;
        if (targetList.length !== (conversationList || []).length) {
          this.$message.warning("历史记录过大，已自动清理最早会话");
        }
        return true;
      } catch (e) {
        this.historyReadOnly = true;
        this.showStorageLimitDialog = true;
        return false;
      }
    },

    loadConversations() {
      const key = this.getHistoryStorageKey();
      this.loadingMap = {};
      this.activeControllers = {};
      const raw = localStorage.getItem(key);
      if (!raw) {
        this.conversationList = [];
        this.currentConversationId = null;
        this.messages = [];
        this.historyReadOnly = false;
        return;
      }
      const size = this.estimateSizeBytes(raw);
      if (size >= 5 * 1024 * 1024) {
        try {
          const list = JSON.parse(raw);
          const shrinked = this.shrinkHistory(Array.isArray(list) ? list : []);
          if (this.tryPersistHistory(shrinked)) {
            this.conversationList = shrinked;
            this.historyReadOnly = false;
            this.currentConversationId = null;
            this.messages = [];
            return;
          }
        } catch (e) {}
        this.historyReadOnly = true;
        this.showStorageLimitDialog = true;
      } else {
        this.historyReadOnly = false;
      }

      try {
        const list = JSON.parse(raw);
        this.conversationList = Array.isArray(list) ? list : [];
        this.currentConversationId = null;
        this.messages = [];
      } catch (e) {
        this.conversationList = [];
        this.currentConversationId = null;
        this.messages = [];
      }
    },

    // 创建新会话（仅本地存储）
    createNewChat() {
      const id = `${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const conv = {
        id,
        title: "新会话",
        messages: [],
        createTime: Date.now(),
        updateTime: Date.now(),
      };
      const next = [conv, ...this.conversationList];
      this.tryPersistHistory(next);
      this.conversationList = next;
      this.currentConversationId = id;
      this.messages = [];
    },

    // 选择会话（仅本地存储）
    selectConversation(conv) {
      this.currentConversationId = conv.id;
      this.messages = Array.isArray(conv.messages) ? conv.messages : [];
      this.scrollToBottom();
      this.scheduleMermaidRender();
    },

    // 处理会话操作（仅本地存储）
    handleConvCommand(command, conv) {
      if (command === "delete") {
        this.abortConversationRequest(conv.id);
        const next = this.conversationList.filter((c) => c.id !== conv.id);
        this.tryPersistHistory(next);
        this.conversationList = next;
        if (this.currentConversationId === conv.id) {
          this.currentConversationId = null;
          this.messages = [];
        }
      }
    },

    isConversationLoading(conversationId) {
      return !!this.loadingMap[conversationId] && !!this.activeControllers[conversationId];
    },

    markConversationLoading(conversationId, loading) {
      if (loading) {
        this.$set(this.loadingMap, conversationId, true);
      } else {
        this.$delete(this.loadingMap, conversationId);
      }
    },

    abortConversationRequest(conversationId) {
      const controller = this.activeControllers[conversationId];
      if (controller && typeof controller.abort === "function") {
        controller.abort();
      }
      this.$delete(this.activeControllers, conversationId);
      this.markConversationLoading(conversationId, false);
    },

    getConversationIndex(conversationId) {
      return this.conversationList.findIndex((c) => c.id === conversationId);
    },

    updateConversationById(conversationId, messages) {
      if (!conversationId) return;
      const next = this.conversationList.map((c) => {
        if (c.id !== conversationId) return c;
        const title = c.title && c.title !== "新会话" ? c.title : (messages[0]?.content || "新会话").slice(0, 20);
        return {
          ...c,
          title,
          messages,
          updateTime: Date.now(),
        };
      });
      this.tryPersistHistory(next);
      this.conversationList = next;
      if (this.currentConversationId === conversationId) {
        this.messages = messages;
      }
    },

    async sendMessage() {
      if (!this.inputMessage.trim()) return;

      const projectId = this.getCurrentProjectId();
      const userId = this.getCurrentUserId();

      if (!projectId) {
        this.$message.error("当前项目ID为空，请重新选择项目后重试");
        return;
      }
      if (!userId) {
        this.$message.error("当前用户ID为空，请重新登录后重试");
        return;
      }

      if (!this.currentConversationId) {
        this.createNewChat();
      }
      const sendingConversationId = this.currentConversationId;
      if (!sendingConversationId || this.isConversationLoading(sendingConversationId)) return;
      const conversationIndex = this.getConversationIndex(sendingConversationId);
      if (conversationIndex < 0) return;
      const baseMessages = Array.isArray(this.conversationList[conversationIndex].messages)
        ? [...this.conversationList[conversationIndex].messages]
        : [];
      const inputMsg = this.inputMessage;
      this.inputMessage = "";

      const userMsg = {
        role: "user",
        content: inputMsg,
        time: Date.now(),
      };
      const assistantMsg = {
        role: "assistant",
        content: "",
        time: Date.now(),
      };
      const sendingMessages = [...baseMessages, userMsg, assistantMsg];
      this.updateConversationById(sendingConversationId, sendingMessages);
      this.markConversationLoading(sendingConversationId, true);
      const controller = new AbortController();
      this.$set(this.activeControllers, sendingConversationId, controller);
      this.scrollToBottom();

      try {
        const response = await fetch(
          this.buildApiUrl("/autotest/ai/chat/stream"),
          {
            method: "POST",
            signal: controller.signal,
            headers: {
              "Content-Type": "application/json",
              token: localStorage.getItem("token"),
            },
            body: JSON.stringify({
              projectId: projectId,
              userId: userId,
              message: inputMsg,
              useRag: this.useRag,
              conversationId: sendingConversationId,
            }),
          }
        );

        if (!response.ok || !response.body) {
          throw new Error(`网络异常或服务错误（HTTP ${response.status}）`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let sseBuffer = "";
        let reachEnd = false;
        let hasDelta = false;
        let lastEventAt = Date.now();
        const readWithTimeout = () =>
          Promise.race([
            reader.read(),
            new Promise((_, reject) =>
              setTimeout(() => reject(new Error("流式响应超时，请重试")), 12000)
            ),
          ]);

        while (true) {
          let done = false;
          let value = null;
          try {
            const readResult = await readWithTimeout();
            done = readResult.done;
            value = readResult.value;
          } catch (e) {
            if (hasDelta) {
              break;
            }
            throw e;
          }
          if (done) break;
          const text = decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
          sseBuffer += text;
          let eventEnd = sseBuffer.indexOf("\n\n");
          while (eventEnd !== -1) {
            const rawEvent = sseBuffer.slice(0, eventEnd);
            sseBuffer = sseBuffer.slice(eventEnd + 2);
            const payload = rawEvent
              .split("\n")
              .filter((line) => line.startsWith("data:"))
              .map((line) => line.replace(/^data:\s*/, ""))
              .join("\n")
              .trim();
            if (payload) {
              let data = null;
              try {
                data = JSON.parse(payload);
              } catch (e) {
                data = null;
              }
              if (!data) {
                eventEnd = sseBuffer.indexOf("\n\n");
                continue;
              }
              if (data.type === "content" && data.delta) {
                hasDelta = true;
                lastEventAt = Date.now();
                sendingMessages[sendingMessages.length - 1].content += data.delta;
                if (this.currentConversationId === sendingConversationId) {
                  this.messages = sendingMessages;
                  this.scrollToBottom();
                  this.scheduleMermaidRender();
                }
              } else if (data.type === "case" && data.case) {
                lastEventAt = Date.now();
                this.generatedCase = JSON.stringify(data.case, null, 2);
                this.caseGenerateStep = 2;
                this.showCaseGenerate = true;
              } else if (data.type === "error") {
                throw new Error(data.message || "AI服务错误");
              } else if (data.type === "end") {
                lastEventAt = Date.now();
                reachEnd = true;
              }
            }
            eventEnd = sseBuffer.indexOf("\n\n");
          }
          if (hasDelta && Date.now() - lastEventAt > 8000) {
            break;
          }
          if (reachEnd) {
            break;
          }
        }
        this.updateConversationById(sendingConversationId, sendingMessages);
      } catch (error) {
        if (error && error.name === "AbortError") {
          const last = sendingMessages[sendingMessages.length - 1];
          if (last && last.role === "assistant" && !last.content) {
            sendingMessages.pop();
            this.updateConversationById(sendingConversationId, sendingMessages);
          }
        } else {
          const errorText = `AI服务调用失败：${error.message || "未知错误"}`;
          sendingMessages.push({
            role: "assistant",
            content: errorText,
            time: Date.now(),
          });
          this.updateConversationById(sendingConversationId, sendingMessages);
          this.scheduleMermaidRender();
          this.$message.error("AI服务调用失败：" + (error.message || "未知错误"));
        }
      } finally {
        this.markConversationLoading(sendingConversationId, false);
        this.$delete(this.activeControllers, sendingConversationId);
        if (this.currentConversationId === sendingConversationId) {
          this.scrollToBottom();
        }
        this.scheduleMermaidRender();
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
        this.handleSendAction();
      }
    },

    handleSendAction() {
      if (this.currentConversationLoading && this.currentConversationId) {
        this.abortConversationRequest(this.currentConversationId);
        return;
      }
      this.sendMessage();
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
      if (!this.markdownIt) {
        return this.escapeHtml(content).replace(/\n/g, "<br>");
      }
      return this.markdownIt.render(content);
    },

    initMarkdown() {
      const md = new MarkdownIt({
        html: false,
        breaks: true,
        linkify: true,
        typographer: false,
      });
      const defaultFence = md.renderer.rules.fence;
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        const info = (token.info || "").trim().toLowerCase();
        if (info === "mermaid") {
          return `<div class="mermaid">${this.escapeHtml(token.content)}</div>`;
        }
        if (defaultFence) {
          return defaultFence(tokens, idx, options, env, self);
        }
        return self.renderToken(tokens, idx, options);
      };
      this.markdownIt = md;
    },

    initMermaid() {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
      });
    },

    scheduleMermaidRender() {
      if (this.mermaidRenderTimer) {
        clearTimeout(this.mermaidRenderTimer);
      }
      this.mermaidRenderTimer = setTimeout(() => {
        this.renderMermaid();
      }, 120);
    },

    async renderMermaid() {
      await this.$nextTick();
      if (!this.$el) return;
      const nodes = this.$el.querySelectorAll(".bubble .mermaid");
      let index = 0;
      for (const node of nodes) {
        if (node.getAttribute("data-rendered") === "1") {
          continue;
        }
        const chartCode = (node.textContent || "").trim();
        if (!chartCode) {
          continue;
        }
        try {
          const chartId = `mmd_${Date.now()}_${index}_${Math.random().toString(16).slice(2)}`;
          const result = await mermaid.render(chartId, chartCode);
          node.innerHTML = result.svg;
        } catch (e) {
          node.innerHTML = `<pre>${this.escapeHtml(chartCode)}</pre>`;
        }
        node.setAttribute("data-rendered", "1");
        index += 1;
      }
    },

    escapeHtml(content) {
      return String(content)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
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
      const projectId = this.getCurrentProjectId();
      if (!projectId) {
        this.knowledgeList = [];
        this.knowledgeTreeData = [];
        return;
      }
      const res = await this.$get(
        `/autotest/ai/knowledge?projectId=${projectId}`
      );
      const data = this.getResponseData(res);
      if (Array.isArray(data)) {
        this.knowledgeList = data;
        this.knowledgeTreeData = this.buildKnowledgeTree(data);
        return;
      }
      if (data && Array.isArray(data.data)) {
        this.knowledgeList = data.data;
        this.knowledgeTreeData = this.buildKnowledgeTree(data.data);
        return;
      }
      this.knowledgeList = [];
      this.knowledgeTreeData = [];
    },

    buildKnowledgeTree(list) {
      const rows = Array.isArray(list) ? list : [];
      const map = {};
      const roots = [];
      rows.forEach((item) => {
        map[item.id] = { ...item, children: [] };
      });
      rows.forEach((item) => {
        const parentId = item.parentId || "0";
        if (parentId !== "0" && map[parentId]) {
          map[parentId].children.push(map[item.id]);
        } else {
          roots.push(map[item.id]);
        }
      });
      return roots;
    },

    handleKnowledgeNodeClick(node) {
      if (!node) return;
      if (node.docType === "folder") {
        this.selectedKnowledgeFolderId = node.id;
      } else {
        this.selectedKnowledgeFolderId = node.parentId || "0";
      }
    },

    openCreateFolderDialog(parentNode) {
      const parentId =
        parentNode && parentNode.id
          ? parentNode.id
          : this.selectedKnowledgeFolderId || "0";
      this.knowledgeDialogMode = "create";
      this.knowledgeForm = {
        id: "",
        parentId: parentId,
        name: "",
        docType: "folder",
        content: "",
      };
      this.showKnowledgeDialog = true;
    },

    openCreateKnowledgeDialog(parentNode) {
      const parentId =
        parentNode && parentNode.id
          ? parentNode.id
          : this.selectedKnowledgeFolderId || "0";
      this.knowledgeDialogMode = "create";
      this.knowledgeForm = {
        id: "",
        parentId: parentId,
        name: "",
        docType: "manual",
        content: "",
      };
      this.showKnowledgeDialog = true;
    },

    async openViewKnowledge(kb) {
      const projectId = this.getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await this.$get(`/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`);
      const detail = this.getResponseData(res);
      if (!detail || typeof detail !== "object") {
        this.$message.error("获取文档详情失败");
        return;
      }
      this.knowledgeDialogMode = "view";
      this.knowledgeForm = {
        id: detail.id || "",
        parentId: detail.parentId || "0",
        name: detail.name || "",
        docType: detail.docType || "manual",
        content: detail.content || "",
      };
      this.showKnowledgeDialog = true;
    },

    async openEditKnowledge(kb) {
      const projectId = this.getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await this.$get(`/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`);
      const detail = this.getResponseData(res);
      if (!detail || typeof detail !== "object") {
        this.$message.error("获取文档详情失败");
        return;
      }
      this.knowledgeDialogMode = "edit";
      this.knowledgeForm = {
        id: detail.id || "",
        parentId: detail.parentId || "0",
        name: detail.name || "",
        docType: detail.docType || "manual",
        content: detail.content || "",
      };
      this.showKnowledgeDialog = true;
    },

    closeKnowledgeDialog() {
      this.knowledgeDialogMode = "create";
      this.knowledgeForm = { id: "", parentId: "0", name: "", docType: "manual", content: "" };
    },

    async saveKnowledge() {
      const projectId = this.getCurrentProjectId();
      const userId = this.getCurrentUserId();
      if (!projectId) {
        this.$message.error("当前项目ID为空，请重新选择项目后重试");
        return;
      }
      if (!this.knowledgeForm.name) {
        this.$message.warning("文档名称不能为空");
        return;
      }
      if (this.knowledgeForm.docType !== "folder" && !this.knowledgeForm.content) {
        this.$message.warning("文档内容不能为空");
        return;
      }

      const saveRes = await this.$post("/autotest/ai/knowledge", {
        id: this.knowledgeForm.id || "",
        projectId: projectId,
        parentId: this.knowledgeForm.parentId || "0",
        name: this.knowledgeForm.name,
        docType: this.knowledgeForm.docType,
        content: this.knowledgeForm.docType === "folder" ? "" : this.knowledgeForm.content,
        sourceType: "manual",
        updateUser: userId,
      });

      const knowledgeId = this.getResponseData(saveRes);

      if (
        typeof knowledgeId === "string" &&
        knowledgeId &&
        this.knowledgeForm.docType !== "folder"
      ) {
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
      this.closeKnowledgeDialog();
      this.loadKnowledgeList();
    },

    knowledgeStatusType(status) {
      if (status === "ready") return "success";
      if (status === "error") return "danger";
      return "warning";
    },

    knowledgeStatusText(status) {
      if (status === "ready") return "已索引";
      if (status === "error") return "索引失败";
      return "待索引";
    },

    formatDocType(docType) {
      if (docType === "manual") return "使用手册";
      if (docType === "guide") return "引导文档";
      if (docType === "api_doc") return "接口文档";
      if (docType === "custom") return "自定义";
      return docType || "-";
    },

    async reindexKnowledge(kb) {
      const projectId = this.getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      await this.$post(`/autotest/ai/knowledge/index/${kb.id}?projectId=${projectId}`);
      this.$message.success("索引提交成功");
      this.loadKnowledgeList();
    },

    async deleteKnowledge(kb) {
      const projectId = this.getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      await this.$delete(`/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`);
      this.$message.success("删除成功");
      this.loadKnowledgeList();
    },

    // 用例生成步骤
    async nextCaseStep() {
      if (this.caseGenerateStep === 0) {
        const projectId = this.getCurrentProjectId();
        if (!projectId) {
          this.$message.error("当前项目ID为空，请重新选择项目后重试");
          return;
        }
        const res = await this.$get(`/autotest/ai/agent/api-list/${projectId}`);
        const data = this.getResponseData(res);
        this.apiList = Array.isArray(data) ? data : [];
        this.caseGenerateStep = 1;
      }
    },

    // 生成用例
    async generateCase() {
      const projectId = this.getCurrentProjectId();
      if (!projectId) {
        this.$message.error("当前项目ID为空，请重新选择项目后重试");
        return;
      }

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

.knowledge-entry {
  padding: 16px 10px;
}

.knowledge-manage {
  padding: 10px 0;
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

.knowledge-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.knowledge-manage >>> .el-tree-node__content,
.knowledge-list >>> .el-tree-node__content {
  height: 36px;
}

.knowledge-node {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.knowledge-node-main {
  min-width: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.knowledge-node-title {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-node-actions {
  display: inline-flex;
  align-items: center;
  gap: 2px;
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

.message.assistant .bubble >>> h1,
.message.assistant .bubble >>> h2,
.message.assistant .bubble >>> h3,
.message.assistant .bubble >>> h4 {
  margin: 10px 0 6px;
  line-height: 1.4;
}

.message.assistant .bubble >>> p {
  margin: 6px 0;
}

.message.assistant .bubble >>> pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
}

.message.assistant .bubble >>> code {
  font-family: Consolas, "Courier New", monospace;
}

.message.assistant .bubble >>> ul,
.message.assistant .bubble >>> ol {
  padding-left: 20px;
  margin: 8px 0;
}

.message.assistant .bubble >>> .mermaid {
  overflow-x: auto;
  max-width: 100%;
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

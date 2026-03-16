/**
 * AI助手页面 - 优化版本
 * 修复流式输出和按钮状态问题
 */
<template>
  <div class="ai-assistant">
    <assistant-sidebar
      :conversation-list="conversationList"
      :current-conversation-id="currentConversationId"
      :history-read-only="historyReadOnly"
      @create-chat="createNewChat"
      @select-conversation="selectConversation"
      @conv-command="handleConvCommand"
      @open-knowledge="openKnowledgeManage"
      @export-history="exportLocalHistory"
      @reset-history="resetLocalHistory"
      @clear-history="clearLocalHistory"
    />

    <assistant-chat-panel
      :use-rag="useRag"
      :current-conversation-id="currentConversationId"
      :messages="messages"
      :input-message="inputMessage"
      :can-send="canSend"
      :is-sending="isSending"
      :render-content="renderContent"
      :format-time="formatTime"
      @update:use-rag="useRag = $event"
      @update-input="inputMessage = $event"
      @create-chat="createNewChat"
      @enter="handleEnter"
      @send-action="handleSendAction"
      @open-case-editor="openCaseEditorFromMessage"
    />

    <!-- 知识库管理对话框 -->
    <el-dialog
      title="知识库管理"
      :visible.sync="showKnowledgeManageDialog"
      width="980px"
      append-to-body
      destroy-on-close
      class="knowledge-manage-dialog"
    >
      <div class="knowledge-manage">
        <div class="knowledge-toolbar">
          <el-button
            size="small"
            icon="el-icon-folder-add"
            @click="openCreateFolderDialog"
          >
            新建目录
          </el-button>
          <el-button
            size="small"
            icon="el-icon-plus"
            type="primary"
            @click="openCreateKnowledgeDialog"
          >
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
              <i
                :class="
                  data.docType === 'folder'
                    ? 'el-icon-folder'
                    : 'el-icon-document'
                "
              ></i>
              <span class="knowledge-node-title">{{
                data.name || "未命名文档"
              }}</span>
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

    <!-- 知识库添加对话框 -->
    <el-dialog
      :title="knowledgeDialogTitle"
      :visible.sync="showKnowledgeDialog"
      width="600px"
      @close="closeKnowledgeDialog"
      class="knowledge-edit-dialog"
    >
      <el-form :model="knowledgeForm" label-width="80px" class="knowledge-form">
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
        <el-form-item
          label="文档内容"
          v-if="knowledgeForm.docType !== 'folder'"
        >
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
        <el-button
          v-if="!isKnowledgeReadonly"
          type="primary"
          @click="saveKnowledge"
        >
          {{ knowledgeForm.docType === "folder" ? "保存目录" : "保存并索引" }}
        </el-button>
      </div>
    </el-dialog>

    <!-- 本地存储容量提示 -->
    <el-dialog
      title="本地存储容量提示"
      :visible.sync="showStorageLimitDialog"
      width="520px"
      class="storage-dialog"
    >
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
        <el-button type="primary" @click="showStorageLimitDialog = false"
          >我知道了</el-button
        >
      </div>
    </el-dialog>

    <el-dialog
      title="Mermaid 预览"
      :visible.sync="showMermaidPreviewDialog"
      width="80%"
      append-to-body
      class="mermaid-dialog"
    >
      <div class="mermaid-preview" v-html="mermaidPreviewSvg"></div>
    </el-dialog>
  </div>
</template>

<script>
import {
  defineComponent,
  getCurrentInstance,
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js/lib/core";
import java from "highlight.js/lib/languages/java";
import python from "highlight.js/lib/languages/python";
import mermaid from "mermaid";
import AssistantSidebar from "./components/AssistantSidebar.vue";
import AssistantChatPanel from "./components/AssistantChatPanel.vue";
import { parseSsePayload } from "./utils/sse";

export default defineComponent({
  name: "AIAssistant",
  components: { AssistantSidebar, AssistantChatPanel },
  setup() {
    const vm = getCurrentInstance().proxy;
    const conversationList = ref([]);
    const knowledgeList = ref([]);
    const currentConversationId = ref("");
    const historyReadOnly = ref(false);
    const showStorageLimitDialog = ref(false);
    const inputMessage = ref("");
    const messages = ref([]);
    const useRag = ref(true);
    const isSending = ref(false);
    const abortController = ref(null);
    const currentStreamReader = ref(null);
    const showKnowledgeDialog = ref(false);
    const showKnowledgeManageDialog = ref(false);
    const selectedKnowledgeFolderId = ref("0");
    const knowledgeTreeData = ref([]);
    const knowledgeDialogMode = ref("create");
    const knowledgeForm = ref({
      id: "",
      parentId: "0",
      name: "",
      docType: "manual",
      content: "",
    });
    const markdownIt = ref(null);
    const mermaidRenderTimer = ref(null);
    const showMermaidPreviewDialog = ref(false);
    const mermaidPreviewSvg = ref("");

    const canSend = computed(() =>
      isSending.value ? true : inputMessage.value.trim().length > 0
    );
    const isKnowledgeReadonly = computed(
      () => knowledgeDialogMode.value === "view"
    );
    const knowledgeDialogTitle = computed(() => {
      if (knowledgeDialogMode.value === "view") return "知识文档详情";
      if (knowledgeDialogMode.value === "edit") return "编辑知识文档";
      return "添加知识库文档";
    });

    const getCurrentProjectId = () => {
      if (vm.$store.state.projectId) return String(vm.$store.state.projectId);
      if (vm.$store.state.userInfo && vm.$store.state.userInfo.lastProject) {
        const lastProject = vm.$store.state.userInfo.lastProject;
        if (typeof lastProject === "string" || typeof lastProject === "number")
          return String(lastProject);
        if (typeof lastProject === "object" && lastProject.id)
          return String(lastProject.id);
      }
      const rawUser = localStorage.getItem("userInfo");
      if (rawUser) {
        try {
          const user = JSON.parse(rawUser);
          if (user && user.lastProject) {
            if (
              typeof user.lastProject === "string" ||
              typeof user.lastProject === "number"
            )
              return String(user.lastProject);
            if (typeof user.lastProject === "object" && user.lastProject.id)
              return String(user.lastProject.id);
          }
        } catch (e) {}
      }
      const projectId = localStorage.getItem("projectId");
      return projectId ? String(projectId) : "";
    };

    const getCurrentUserId = () => {
      if (vm.$store.state.userInfo && vm.$store.state.userInfo.id)
        return String(vm.$store.state.userInfo.id);
      const rawUser = localStorage.getItem("userInfo");
      if (rawUser) {
        try {
          const user = JSON.parse(rawUser);
          if (user && user.id) return String(user.id);
        } catch (e) {}
      }
      const userId = localStorage.getItem("userId");
      return userId ? String(userId) : "";
    };

    const buildApiUrl = (path) => {
      const base =
        (vm.$axios && vm.$axios.defaults && vm.$axios.defaults.baseURL) || "";
      if (!base || base === "/") return path;
      const normalizedBase = base.endsWith("/") ? base.slice(0, -1) : base;
      const normalizedPath = path.startsWith("/") ? path : `/${path}`;
      return `${normalizedBase}${normalizedPath}`;
    };

    const getHistoryStorageKey = () => {
      const projectId = getCurrentProjectId();
      const userId = getCurrentUserId();
      if (projectId && userId)
        return `ai_chat_history_v1:${projectId}:${userId}`;
      const token = localStorage.getItem("token") || "anonymous";
      const tokenTail = token.slice(-12);
      return `ai_chat_history_v1:${projectId || "no_project"}:${
        userId || tokenTail
      }`;
    };

    const estimateSizeBytes = (text) => {
      try {
        return new Blob([text]).size;
      } catch (e) {
        return (text || "").length;
      }
    };

    const shrinkHistory = (value) => {
      const list = Array.isArray(value) ? [...value] : [];
      let json = JSON.stringify(list);
      let size = estimateSizeBytes(json);
      while (size >= 4.5 * 1024 * 1024 && list.length > 1) {
        list.pop();
        json = JSON.stringify(list);
        size = estimateSizeBytes(json);
      }
      if (size >= 4.5 * 1024 * 1024 && list.length === 1) {
        const one = list[0];
        const msgs = Array.isArray(one.messages) ? [...one.messages] : [];
        while (msgs.length > 2 && size >= 4.5 * 1024 * 1024) {
          msgs.shift();
          one.messages = msgs;
          json = JSON.stringify(list);
          size = estimateSizeBytes(json);
        }
      }
      return list;
    };

    const tryPersistHistory = (value) => {
      const key = getHistoryStorageKey();
      let targetList = value || [];
      let json = JSON.stringify(targetList);
      if (estimateSizeBytes(json) >= 5 * 1024 * 1024) {
        targetList = shrinkHistory(targetList);
        json = JSON.stringify(targetList);
      }
      try {
        localStorage.setItem(key, json);
        historyReadOnly.value = false;
        if (targetList.length !== (value || []).length)
          vm.$message.warning("历史记录过大，已自动清理最早会话");
        return true;
      } catch (e) {
        historyReadOnly.value = true;
        showStorageLimitDialog.value = true;
        return false;
      }
    };

    const loadConversations = () => {
      const key = getHistoryStorageKey();
      const raw = localStorage.getItem(key);
      if (!raw) {
        conversationList.value = [];
        currentConversationId.value = "";
        messages.value = [];
        historyReadOnly.value = false;
        return;
      }
      if (estimateSizeBytes(raw) >= 5 * 1024 * 1024) {
        try {
          const list = JSON.parse(raw);
          const shrinked = shrinkHistory(Array.isArray(list) ? list : []);
          if (tryPersistHistory(shrinked)) {
            conversationList.value = shrinked;
            currentConversationId.value = "";
            messages.value = [];
            return;
          }
        } catch (e) {}
        historyReadOnly.value = true;
        showStorageLimitDialog.value = true;
      } else {
        historyReadOnly.value = false;
      }
      try {
        const list = JSON.parse(raw);
        conversationList.value = Array.isArray(list) ? list : [];
      } catch (e) {
        conversationList.value = [];
      }
      currentConversationId.value = "";
      messages.value = [];
    };

    const updateConversationById = (conversationId, msgs) => {
      if (!conversationId) return;
      const next = conversationList.value.map((item) => {
        if (item.id !== conversationId) return item;
        const title =
          item.title && item.title !== "新会话"
            ? item.title
            : (msgs[0]?.content || "新会话").slice(0, 20);
        return { ...item, title, messages: [...msgs], updateTime: Date.now() };
      });
      tryPersistHistory(next);
      conversationList.value = next;
      if (currentConversationId.value === conversationId)
        messages.value = [...msgs];
    };

    const createNewChat = () => {
      const id = `${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const conv = {
        id,
        title: "新会话",
        messages: [],
        createTime: Date.now(),
        updateTime: Date.now(),
      };
      const next = [conv, ...conversationList.value];
      tryPersistHistory(next);
      conversationList.value = next;
      currentConversationId.value = id;
      messages.value = [];
    };

    const stopCurrentStream = () => {
      if (abortController.value) {
        abortController.value.abort();
        abortController.value = null;
      }
      if (currentStreamReader.value) {
        try {
          currentStreamReader.value.cancel();
        } catch (e) {}
        currentStreamReader.value = null;
      }
      isSending.value = false;
    };

    const scrollToBottom = () => {
      nextTick(() => {
        const panel = vm.$el.querySelector(".message-area");
        if (panel) panel.scrollTop = panel.scrollHeight;
      });
    };

    const selectConversation = (conv) => {
      currentConversationId.value = conv.id;
      messages.value = Array.isArray(conv.messages) ? [...conv.messages] : [];
      scrollToBottom();
      scheduleMermaidRender();
    };

    const handleConvCommand = (command, conv) => {
      if (command !== "delete") return;
      stopCurrentStream();
      const next = conversationList.value.filter((item) => item.id !== conv.id);
      tryPersistHistory(next);
      conversationList.value = next;
      if (currentConversationId.value === conv.id) {
        currentConversationId.value = "";
        messages.value = [];
      }
    };

    const buildHistoryMessages = (list) =>
      (Array.isArray(list) ? list : [])
        .filter(
          (item) =>
            item &&
            (item.role === "user" || item.role === "assistant") &&
            item.content &&
            !item.interrupted &&
            !String(item.content).startsWith("AI服务调用失败：")
        )
        .map((item) => ({ role: item.role, content: item.content }));

    const sendMessage = async () => {
      if (!inputMessage.value.trim()) return;
      const projectId = getCurrentProjectId();
      if (!projectId) {
        vm.$message.error("当前项目ID为空，请重新选择项目后重试");
        return;
      }
      if (!currentConversationId.value) createNewChat();
      if (isSending.value) {
        vm.$message.warning("请等待当前对话完成");
        return;
      }
      const sendingConversationId = currentConversationId.value;
      const conversationIndex = conversationList.value.findIndex(
        (item) => item.id === sendingConversationId
      );
      if (conversationIndex < 0) return;
      const baseMessages = Array.isArray(
        conversationList.value[conversationIndex].messages
      )
        ? [...conversationList.value[conversationIndex].messages]
        : [];
      const inputMsg = inputMessage.value;
      inputMessage.value = "";
      const userMsg = { role: "user", content: inputMsg, time: Date.now() };
      const assistantMsg = { role: "assistant", content: "", time: Date.now() };
      const sendingMessages = [...baseMessages, userMsg, assistantMsg];
      updateConversationById(sendingConversationId, sendingMessages);
      isSending.value = true;
      abortController.value = new AbortController();
      scrollToBottom();
      try {
        const response = await fetch(buildApiUrl("/autotest/ai/chat/stream"), {
          method: "POST",
          signal: abortController.value.signal,
          headers: {
            "Content-Type": "application/json",
            token: localStorage.getItem("token"),
          },
          body: JSON.stringify({
            projectId,
            userId: getCurrentUserId(),
            message: inputMsg,
            useRag: useRag.value,
            messages: buildHistoryMessages([...baseMessages, userMsg]),
          }),
        });
        if (!response.ok || !response.body)
          throw new Error(`网络异常或服务错误（HTTP ${response.status}）`);
        const contentType = String(response.headers.get("content-type") || "");
        if (!contentType.includes("text/event-stream"))
          throw new Error("AI服务未返回SSE流，请检查后端流式配置");
        const reader = response.body.getReader();
        currentStreamReader.value = reader;
        const decoder = new TextDecoder();
        let sseBuffer = "";
        let reachEnd = false;
        let lastEventAt = Date.now();
        const idleTimeoutMs = 120000;
        const readWithTimeout = () =>
          new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
              const idle = Date.now() - lastEventAt;
              reject(
                new Error(
                  idle >= idleTimeoutMs
                    ? "流式响应超时，请重试"
                    : "流式响应中断，请重试"
                )
              );
            }, idleTimeoutMs);
            reader
              .read()
              .then((result) => {
                clearTimeout(timer);
                resolve(result);
              })
              .catch((error) => {
                clearTimeout(timer);
                reject(error);
              });
          });
        while (true) {
          const readResult = await readWithTimeout();
          if (readResult.done) break;
          sseBuffer += decoder
            .decode(readResult.value, { stream: true })
            .replace(/\r\n/g, "\n");
          const parsed = parseSsePayload(sseBuffer);
          sseBuffer = parsed.rest;
          for (const data of parsed.events) {
            lastEventAt = Date.now();
            if (data.type === "content" && data.delta) {
              const last = sendingMessages[sendingMessages.length - 1];
              if (last && last.role === "assistant") {
                last.content += data.delta;
                messages.value = [...sendingMessages];
                scrollToBottom();
              }
            } else if (data.type === "case" && data.case) {
              const last = sendingMessages[sendingMessages.length - 1];
              if (last) {
                last.caseData = data.case;
                const apiIds = []
                  .concat(Array.isArray(data.api_ids) ? data.api_ids : [])
                  .concat(
                    Array.isArray(data.created_api_ids)
                      ? data.created_api_ids
                      : []
                  )
                  .filter(Boolean);
                last.apiIds = Array.from(new Set(apiIds));
                messages.value = [...sendingMessages];
              }
            } else if (data.type === "error") {
              throw new Error(data.message || "AI服务错误");
            } else if (data.type === "end") {
              reachEnd = true;
              break;
            }
          }
          if (reachEnd) break;
        }
        updateConversationById(sendingConversationId, sendingMessages);
      } catch (error) {
        if (error && error.name === "AbortError") {
          const last = sendingMessages[sendingMessages.length - 1];
          if (last && last.role === "assistant" && !last.content) {
            sendingMessages.pop();
            updateConversationById(sendingConversationId, sendingMessages);
          } else if (last && last.role === "assistant") {
            last.interrupted = true;
            updateConversationById(sendingConversationId, sendingMessages);
          }
        } else {
          const errorText = `AI服务调用失败：${error.message || "未知错误"}`;
          sendingMessages.push({
            role: "assistant",
            content: errorText,
            time: Date.now(),
          });
          updateConversationById(sendingConversationId, sendingMessages);
          vm.$message.error("AI服务调用失败：" + (error.message || "未知错误"));
        }
      } finally {
        isSending.value = false;
        abortController.value = null;
        currentStreamReader.value = null;
        scrollToBottom();
        scheduleMermaidRender();
      }
    };

    const exportLocalHistory = () => {
      const raw = localStorage.getItem(getHistoryStorageKey()) || "[]";
      const blob = new Blob([raw], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ai_history_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    };

    const resetLocalHistory = () => {
      stopCurrentStream();
      localStorage.removeItem(getHistoryStorageKey());
      conversationList.value = [];
      currentConversationId.value = "";
      messages.value = [];
      historyReadOnly.value = false;
      showStorageLimitDialog.value = false;
      vm.$message.success("已重置本地历史对话");
    };

    const clearLocalHistory = () => {
      if (historyReadOnly.value) {
        vm.$message.warning("当前为只读模式，请先重置或导出后再操作");
        return;
      }
      stopCurrentStream();
      if (!tryPersistHistory([])) return;
      conversationList.value = [];
      currentConversationId.value = "";
      messages.value = [];
      vm.$message.success("已清空本地历史对话");
    };

    const handleEnter = (e) => {
      if (!e.shiftKey) {
        e.preventDefault();
        handleSendAction();
      }
    };

    const handleSendAction = () => {
      if (isSending.value) {
        stopCurrentStream();
        vm.$message.info("已停止生成");
        return;
      }
      sendMessage();
    };

    const escapeHtml = (content) =>
      String(content)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

    const renderContent = (content) => {
      if (!content) return "";
      if (!markdownIt.value) return escapeHtml(content).replace(/\n/g, "<br>");
      return markdownIt.value.render(content);
    };

    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      return `${date.getHours().toString().padStart(2, "0")}:${date
        .getMinutes()
        .toString()
        .padStart(2, "0")}`;
    };

    const getResponseData = (res) => {
      if (!res || !res.data) return null;
      let current = res.data;
      if (Object.prototype.hasOwnProperty.call(current, "data"))
        current = current.data;
      while (
        current &&
        typeof current === "object" &&
        !Array.isArray(current) &&
        Object.keys(current).length === 1 &&
        Object.prototype.hasOwnProperty.call(current, "data")
      )
        current = current.data;
      return current;
    };

    const buildKnowledgeTree = (list) => {
      const rows = Array.isArray(list) ? list : [];
      const map = {};
      const roots = [];
      rows.forEach((item) => {
        map[item.id] = { ...item, children: [] };
      });
      rows.forEach((item) => {
        const parentId = item.parentId || "0";
        if (parentId !== "0" && map[parentId])
          map[parentId].children.push(map[item.id]);
        else roots.push(map[item.id]);
      });
      return roots;
    };

    const loadKnowledgeList = async () => {
      const projectId = getCurrentProjectId();
      if (!projectId) {
        knowledgeList.value = [];
        knowledgeTreeData.value = [];
        return;
      }
      const res = await vm.$get(
        `/autotest/ai/knowledge?projectId=${projectId}`
      );
      const data = getResponseData(res);
      if (Array.isArray(data)) {
        knowledgeList.value = data;
        knowledgeTreeData.value = buildKnowledgeTree(data);
        return;
      }
      if (data && Array.isArray(data.data)) {
        knowledgeList.value = data.data;
        knowledgeTreeData.value = buildKnowledgeTree(data.data);
        return;
      }
      knowledgeList.value = [];
      knowledgeTreeData.value = [];
    };

    const openKnowledgeManage = () => {
      showKnowledgeManageDialog.value = true;
      loadKnowledgeList();
    };

    const handleKnowledgeNodeClick = (node) => {
      if (!node) return;
      selectedKnowledgeFolderId.value =
        node.docType === "folder" ? node.id : node.parentId || "0";
    };

    const openCreateFolderDialog = (parentNode) => {
      const parentId =
        parentNode && parentNode.id
          ? parentNode.id
          : selectedKnowledgeFolderId.value || "0";
      knowledgeDialogMode.value = "create";
      knowledgeForm.value = {
        id: "",
        parentId,
        name: "",
        docType: "folder",
        content: "",
      };
      showKnowledgeDialog.value = true;
    };

    const openCreateKnowledgeDialog = (parentNode) => {
      const parentId =
        parentNode && parentNode.id
          ? parentNode.id
          : selectedKnowledgeFolderId.value || "0";
      knowledgeDialogMode.value = "create";
      knowledgeForm.value = {
        id: "",
        parentId,
        name: "",
        docType: "manual",
        content: "",
      };
      showKnowledgeDialog.value = true;
    };

    const openViewKnowledge = async (kb) => {
      const projectId = getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await vm.$get(
        `/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`
      );
      const detail = getResponseData(res);
      if (!detail || typeof detail !== "object") {
        vm.$message.error("获取文档详情失败");
        return;
      }
      knowledgeDialogMode.value = "view";
      knowledgeForm.value = {
        id: detail.id || "",
        parentId: detail.parentId || "0",
        name: detail.name || "",
        docType: detail.docType || "manual",
        content: detail.content || "",
      };
      showKnowledgeDialog.value = true;
    };

    const openEditKnowledge = async (kb) => {
      const projectId = getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await vm.$get(
        `/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`
      );
      const detail = getResponseData(res);
      if (!detail || typeof detail !== "object") {
        vm.$message.error("获取文档详情失败");
        return;
      }
      knowledgeDialogMode.value = "edit";
      knowledgeForm.value = {
        id: detail.id || "",
        parentId: detail.parentId || "0",
        name: detail.name || "",
        docType: detail.docType || "manual",
        content: detail.content || "",
      };
      showKnowledgeDialog.value = true;
    };

    const closeKnowledgeDialog = () => {
      knowledgeDialogMode.value = "create";
      knowledgeForm.value = {
        id: "",
        parentId: "0",
        name: "",
        docType: "manual",
        content: "",
      };
    };

    const saveKnowledge = async () => {
      const projectId = getCurrentProjectId();
      if (!projectId) {
        vm.$message.error("当前项目ID为空，请重新选择项目后重试");
        return;
      }
      if (!knowledgeForm.value.name) {
        vm.$message.warning("文档名称不能为空");
        return;
      }
      if (
        knowledgeForm.value.docType !== "folder" &&
        !knowledgeForm.value.content
      ) {
        vm.$message.warning("文档内容不能为空");
        return;
      }
      const saveRes = await vm.$post("/autotest/ai/knowledge", {
        id: knowledgeForm.value.id || "",
        projectId,
        parentId: knowledgeForm.value.parentId || "0",
        name: knowledgeForm.value.name,
        docType: knowledgeForm.value.docType,
        content:
          knowledgeForm.value.docType === "folder"
            ? ""
            : knowledgeForm.value.content,
        sourceType: "manual",
        updateUser: getCurrentUserId(),
      });
      const knowledgeId = getResponseData(saveRes);
      if (knowledgeId === null || knowledgeId === undefined) {
        vm.$message.error("保存知识库失败");
        return;
      }
      if (
        typeof knowledgeId === "string" &&
        knowledgeId &&
        knowledgeForm.value.docType !== "folder"
      ) {
        try {
          const indexRes = await vm.$post(
            `/autotest/ai/knowledge/index/${knowledgeId}?projectId=${projectId}`
          );
          const indexData = getResponseData(indexRes);
          if (indexData && indexData.indexedStatus === "degraded")
            vm.$message.warning(
              "保存成功，但索引降级失败，请检查Embedding配置"
            );
          else vm.$message.success("保存成功，索引已完成");
        } catch (e) {
          vm.$message.warning("保存成功，但索引提交失败");
        }
      } else {
        vm.$message.success("保存成功");
      }
      showKnowledgeDialog.value = false;
      closeKnowledgeDialog();
      loadKnowledgeList();
    };

    const knowledgeStatusType = (status) => {
      if (status === "ready") return "success";
      if (status === "error") return "danger";
      if (status === "degraded") return "warning";
      return "warning";
    };

    const knowledgeStatusText = (status) => {
      if (status === "ready") return "已索引";
      if (status === "error") return "索引失败";
      if (status === "degraded") return "索引降级";
      return "待索引";
    };

    const reindexKnowledge = async (kb) => {
      const projectId = getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await vm.$post(
        `/autotest/ai/knowledge/index/${kb.id}?projectId=${projectId}`
      );
      const result = getResponseData(res);
      if (result === null || result === undefined) {
        vm.$message.error("索引失败");
        return;
      }
      vm.$message.success("索引提交成功");
      loadKnowledgeList();
    };

    const deleteKnowledge = async (kb) => {
      const projectId = getCurrentProjectId();
      if (!projectId || !kb || !kb.id) return;
      const res = await vm.$delete(
        `/autotest/ai/knowledge/${kb.id}?projectId=${projectId}`
      );
      const result = getResponseData(res);
      if (result === null || result === undefined) {
        vm.$message.error("删除失败");
        return;
      }
      vm.$message.success("删除成功");
      loadKnowledgeList();
    };

    const openCaseEditorFromMessage = (msg) => {
      if (!msg || !msg.caseData) {
        vm.$message.warning("暂无可跳转的用例");
        return;
      }
      const projectId = getCurrentProjectId();
      localStorage.setItem(
        `ai_case_draft_v1:${projectId || "default"}`,
        JSON.stringify(msg.caseData)
      );
      vm.$router.push({ path: "/caseCenter/caseManage/apiCase/add" });
    };

    const initMarkdown = () => {
      hljs.registerLanguage("java", java);
      hljs.registerLanguage("python", python);
      const md = new MarkdownIt({
        html: false,
        breaks: true,
        linkify: true,
        typographer: false,
        highlight: (str, lang) => {
          if (lang && hljs.getLanguage(lang)) {
            return `<pre class="hljs"><code>${
              hljs.highlight(str, { language: lang }).value
            }</code></pre>`;
          }
          return `<pre class="hljs"><code>${md.utils.escapeHtml(
            str
          )}</code></pre>`;
        },
      });
      const defaultFence = md.renderer.rules.fence;
      md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        const info = (token.info || "").trim().toLowerCase();
        if (info === "mermaid")
          return `<div class="mermaid">${escapeHtml(token.content)}</div>`;
        if (defaultFence) return defaultFence(tokens, idx, options, env, self);
        return self.renderToken(tokens, idx, options);
      };
      markdownIt.value = md;
    };

    const initMermaid = () => {
      mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
    };

    const renderMermaid = async () => {
      await nextTick();
      if (!vm.$el) return;
      const nodes = vm.$el.querySelectorAll(".assistant-markdown .mermaid");
      let index = 0;
      for (const node of nodes) {
        if (node.getAttribute("data-rendered") === "1") continue;
        const chartCode = (node.textContent || "").trim();
        if (!chartCode) continue;
        try {
          const result = await mermaid.render(
            `mmd_${Date.now()}_${index}_${Math.random().toString(16).slice(2)}`,
            chartCode
          );
          node.innerHTML = result.svg;
          node.classList.add("clickable-mermaid");
          node.addEventListener("click", () => {
            mermaidPreviewSvg.value = result.svg;
            showMermaidPreviewDialog.value = true;
          });
        } catch (e) {
          node.innerHTML = `<pre>${escapeHtml(chartCode)}</pre>`;
        }
        node.setAttribute("data-rendered", "1");
        index += 1;
      }
    };

    const scheduleMermaidRender = () => {
      if (mermaidRenderTimer.value) clearTimeout(mermaidRenderTimer.value);
      mermaidRenderTimer.value = setTimeout(() => renderMermaid(), 120);
    };

    onMounted(() => {
      initMarkdown();
      initMermaid();
      loadConversations();
      loadKnowledgeList();
      scheduleMermaidRender();
    });

    onBeforeUnmount(() => {
      stopCurrentStream();
      if (mermaidRenderTimer.value) clearTimeout(mermaidRenderTimer.value);
    });

    return {
      conversationList,
      currentConversationId,
      historyReadOnly,
      showStorageLimitDialog,
      inputMessage,
      messages,
      useRag,
      isSending,
      showKnowledgeDialog,
      showKnowledgeManageDialog,
      selectedKnowledgeFolderId,
      knowledgeTreeData,
      knowledgeDialogMode,
      knowledgeForm,
      showMermaidPreviewDialog,
      mermaidPreviewSvg,
      canSend,
      isKnowledgeReadonly,
      knowledgeDialogTitle,
      createNewChat,
      selectConversation,
      handleConvCommand,
      openKnowledgeManage,
      exportLocalHistory,
      resetLocalHistory,
      clearLocalHistory,
      handleEnter,
      handleSendAction,
      renderContent,
      formatTime,
      handleKnowledgeNodeClick,
      openCreateFolderDialog,
      openCreateKnowledgeDialog,
      openViewKnowledge,
      openEditKnowledge,
      closeKnowledgeDialog,
      saveKnowledge,
      knowledgeStatusType,
      knowledgeStatusText,
      reindexKnowledge,
      deleteKnowledge,
      openCaseEditorFromMessage,
    };
  },
});
</script>

    <style scoped>
.ai-assistant {
  display: flex;
  width: 100%;
  height: calc(100vh - 56px);
  min-height: 640px;
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

.conversation-list,
.knowledge-list {
  padding: 10px;
}
.conversation-list {
  flex: 1;
  overflow-y: auto;
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

.message.assistant .content {
  max-width: 86%;
  margin-left: 0;
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

.assistant-markdown {
  line-height: 1.6;
  word-break: break-word;
}

.assistant-markdown >>> h1,
.assistant-markdown >>> h2,
.assistant-markdown >>> h3,
.assistant-markdown >>> h4 {
  margin: 10px 0 6px;
  line-height: 1.4;
}

.assistant-markdown >>> p {
  margin: 6px 0;
}

.assistant-markdown >>> pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
}

.assistant-markdown >>> code {
  font-family: Consolas, "Courier New", monospace;
}

.assistant-markdown >>> ul,
.assistant-markdown >>> ol {
  padding-left: 20px;
  margin: 8px 0;
}

.assistant-markdown >>> .mermaid {
  overflow-x: auto;
  max-width: 100%;
  cursor: zoom-in;
}

.assistant-markdown >>> .clickable-mermaid {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 8px;
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

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 20px;
}

/* AI Cards Styles */
.ai-card {
  margin-top: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-header {
  padding: 10px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-header.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.card-body {
  padding: 15px;
}

.card-body p {
  margin: 0 0 10px;
  line-height: 1.5;
  color: #606266;
}

.interface-list {
  margin: 0 0 15px;
  padding: 0;
  list-style: none;
}

.interface-list li {
  margin-bottom: 5px;
  font-family: monospace;
  font-size: 13px;
  color: #606266;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.case-edit-form {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.case-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.case-step-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-field {
  flex: 1;
}

.step-field.short {
  max-width: 90px;
}

.step-field.api-id {
  max-width: 120px;
}

.mermaid-preview {
  width: 100%;
  overflow: auto;
}

.mermaid-preview >>> svg {
  max-width: 100%;
}

.knowledge-manage-dialog :deep(.el-dialog),
.knowledge-edit-dialog :deep(.el-dialog),
.storage-dialog :deep(.el-dialog),
.mermaid-dialog :deep(.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
}

.knowledge-manage-dialog :deep(.el-dialog__header),
.knowledge-edit-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #edf1f7;
  background: #f8fbff;
}

.knowledge-manage-dialog :deep(.el-dialog__body),
.knowledge-edit-dialog :deep(.el-dialog__body) {
  padding-top: 16px;
}

.knowledge-form :deep(.el-input__inner),
.knowledge-form :deep(.el-textarea__inner),
.knowledge-form :deep(.el-select .el-input__inner) {
  border-radius: 8px;
}
</style>

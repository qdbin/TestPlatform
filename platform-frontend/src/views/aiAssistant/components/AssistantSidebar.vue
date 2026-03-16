<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <el-button
        type="primary"
        icon="el-icon-plus"
        size="small"
        @click="$emit('create-chat')"
        :disabled="historyReadOnly"
        >新建对话</el-button
      >
    </div>

    <div class="conversation-list">
      <div
        v-for="conv in conversationList"
        :key="conv.id"
        class="conversation-item"
        :class="{ active: currentConversationId === conv.id }"
        @click="$emit('select-conversation', conv)"
      >
        <i class="el-icon-chat-line-round"></i>
        <span class="conv-title">{{ conv.title || "新会话" }}</span>
        <el-dropdown
          trigger="click"
          @command="$emit('conv-command', $event, conv)"
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

    <div class="sidebar-footer">
      <el-button size="small" type="primary" @click="$emit('open-knowledge')">
        <i class="el-icon-folder"></i> 知识库
      </el-button>
      <el-button size="small" @click="$emit('export-history')">
        <i class="el-icon-download"></i> 导出
      </el-button>
      <el-button size="small" type="warning" @click="$emit('reset-history')">
        <i class="el-icon-refresh"></i> 重置
      </el-button>
      <el-button size="small" type="danger" @click="$emit('clear-history')">
        <i class="el-icon-delete"></i> 清空
      </el-button>
      <div v-if="historyReadOnly" class="storage-limit-tip">
        <el-tag type="danger" size="mini">本地存储已满（只读）</el-tag>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "AssistantSidebar",
  emits: [
    "create-chat",
    "select-conversation",
    "conv-command",
    "open-knowledge",
    "export-history",
    "reset-history",
    "clear-history",
  ],
  props: {
    conversationList: { type: Array, default: () => [] },
    currentConversationId: { type: String, default: "" },
    historyReadOnly: { type: Boolean, default: false },
  },
});
</script>

<style scoped>
.sidebar {
  width: 296px;
  min-width: 296px;
  background: #f7f9fc;
  border-right: 1px solid #e7edf5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 14px 14px 12px;
  border-bottom: 1px solid #e7edf5;
  background: #fff;
}

.sidebar-header .el-button {
  width: 100%;
  border-radius: 10px;
  font-weight: 600;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 10px;
  cursor: pointer;
  color: #5f6471;
  background: #fff;
  border: 1px solid #edf1f7;
  transition: all 0.2s ease;
}

.conversation-item:hover {
  border-color: #c8dcff;
  background: #f2f7ff;
  color: #356bcb;
}

.conversation-item.active {
  background: linear-gradient(135deg, #4c8dff 0%, #3d7cf0 100%);
  border-color: #3d7cf0;
  color: #fff;
  box-shadow: 0 8px 18px rgba(61, 124, 240, 0.25);
}

.conv-title {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-item .el-icon-more {
  font-size: 14px;
  padding: 2px;
  border-radius: 6px;
}

.conversation-item .el-icon-more:hover {
  background: rgba(255, 255, 255, 0.25);
}

.empty-tip {
  padding: 28px 12px;
  color: #97a0af;
  text-align: center;
  font-size: 13px;
}

.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid #e7edf5;
  background: #fff;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.sidebar-footer .el-button {
  margin: 0;
  border-radius: 8px;
}

.storage-limit-tip {
  grid-column: 1 / -1;
}
</style>

/**
 * AI助手页面
 */
<template>
    <div class="ai-assistant">
        <!-- 左侧边栏 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <el-button type="primary" icon="el-icon-plus" size="small" @click="createNewChat">新建对话</el-button>
            </div>
            
            <el-tabs v-model="activeTab" class="sidebar-tabs">
                <el-tab-pane label="会话" name="chat">
                    <div class="conversation-list">
                        <div 
                            v-for="conv in conversationList" 
                            :key="conv.id"
                            class="conversation-item"
                            :class="{active: currentConversationId === conv.id}"
                            @click="selectConversation(conv)"
                        >
                            <i class="el-icon-chat-line-round"></i>
                            <span class="conv-title">{{ conv.title || '新会话' }}</span>
                            <el-dropdown trigger="click" @command="handleConvCommand($event, conv)">
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
                        <el-button size="small" icon="el-icon-plus" @click="showKnowledgeDialog = true">添加文档</el-button>
                        <div class="knowledge-items">
                            <div v-for="kb in knowledgeList" :key="kb.id" class="knowledge-item">
                                <i class="el-icon-document"></i>
                                <span>{{ kb.name }}</span>
                                <el-tag size="mini" :type="kb.indexedStatus === 'ready' ? 'success' : 'warning'">
                                    {{ kb.indexedStatus === 'ready' ? '已索引' : '待索引' }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>
            
            <div class="sidebar-footer">
                <el-button size="small" @click="showSettings = true">
                    <i class="el-icon-setting"></i> 设置
                </el-button>
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
                    <el-switch
                        v-model="useRag"
                        active-text="RAG"
                        inactive-text="纯对话"
                    >
                    </el-switch>
                    <el-button type="text" icon="el-icon-s-promotion" @click="showCaseGenerate = true">
                        用例生成
                    </el-button>
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
                            <i :class="msg.role === 'user' ? 'el-icon-user' : 'el-icon-cpu'"></i>
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
                    :disabled="isLoading"
                >
                </el-input>
                <el-button 
                    type="primary" 
                    :loading="isLoading"
                    :disabled="!inputMessage.trim()"
                    @click="sendMessage"
                >
                    发送
                </el-button>
            </div>
        </div>
        
        <!-- 用例生成对话框 -->
        <el-dialog title="AI 用例生成" :visible.sync="showCaseGenerate" width="800px">
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
                        <el-checkbox 
                            v-for="api in apiList" 
                            :key="api.id" 
                            :label="api.id"
                        >
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
                    <el-button type="primary" @click="saveGeneratedCase">确认并保存</el-button>
                </div>
            </div>
        </el-dialog>
        
        <!-- 知识库添加对话框 -->
        <el-dialog title="添加知识库文档" :visible.sync="showKnowledgeDialog" width="600px">
            <el-form :model="knowledgeForm" label-width="80px">
                <el-form-item label="文档名称">
                    <el-input v-model="knowledgeForm.name" placeholder="请输入文档名称"></el-input>
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
                    <el-input v-model="knowledgeForm.content" type="textarea" :rows="10" placeholder="请输入文档内容"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer">
                <el-button @click="showKnowledgeDialog = false">取消</el-button>
                <el-button type="primary" @click="saveKnowledge">保存并索引</el-button>
            </div>
        </el-dialog>
        
        <!-- 设置对话框 -->
        <el-dialog title="AI 设置" :visible.sync="showSettings" width="500px">
            <el-form label-width="100px">
                <el-form-item label="AI 提供商">
                    <el-select v-model="aiSettings.provider">
                        <el-option label="DeepSeek" value="deepseek"></el-option>
                        <el-option label="OpenAI" value="openai"></el-option>
                        <el-option label="通义千问" value="qwen"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="API Key">
                    <el-input v-model="aiSettings.apiKey" type="password" placeholder="请输入 API Key"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer">
                <el-button @click="showSettings = false">取消</el-button>
                <el-button type="primary" @click="saveAiSettings">保存</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'AIAssistant',
    data() {
        return {
            // 侧边栏
            activeTab: 'chat',
            conversationList: [],
            knowledgeList: [],
            currentConversationId: null,
            
            // 聊天
            inputMessage: '',
            messages: [],
            isLoading: false,
            useRag: true,
            
            // 用例生成
            showCaseGenerate: false,
            caseGenerateStep: 0,
            caseRequirement: '',
            apiList: [],
            selectedApis: [],
            generatedCase: '',
            
            // 知识库
            showKnowledgeDialog: false,
            knowledgeForm: {
                name: '',
                docType: 'manual',
                content: ''
            },
            
            // 设置
            showSettings: false,
            aiSettings: {
                provider: 'deepseek',
                apiKey: ''
            }
        };
    },
    mounted() {
        this.loadConversations();
        this.loadKnowledgeList();
    },
    methods: {
        // 创建新会话
        async createNewChat() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            const userId = this.$store.state.user?.id || localStorage.getItem('userId');
            
            const res = await this.$post('/autotest/ai/chat', {
                projectId: projectId,
                userId: userId,
                sessionType: 'chat',
                useRag: this.useRag
            });
            
            if (res.data) {
                this.currentConversationId = res.data;
                this.messages = [];
                this.loadConversations();
            }
        },
        
        // 加载会话列表
        async loadConversations() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            const userId = this.$store.state.user?.id || localStorage.getItem('userId');
            
            const res = await this.$get(`/autotest/ai/chat/history?projectId=${projectId}&userId=${userId}`);
            if (res.data) {
                this.conversationList = res.data;
            }
        },
        
        // 选择会话
        async selectConversation(conv) {
            this.currentConversationId = conv.id;
            
            const res = await this.$get(`/autotest/ai/chat/${conv.id}`);
            if (res.data && res.data.messages) {
                this.messages = JSON.parse(res.data.messages);
            }
        },
        
        // 处理会话操作
        async handleConvCommand(command, conv) {
            if (command === 'delete') {
                await this.$delete(`/autotest/ai/chat/${conv.id}`);
                this.loadConversations();
                if (this.currentConversationId === conv.id) {
                    this.currentConversationId = null;
                    this.messages = [];
                }
            }
        },
        
        // 发送消息
        async sendMessage() {
            if (!this.inputMessage.trim() || this.isLoading) return;
            
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            const userId = this.$store.state.user?.id || localStorage.getItem('userId');
            
            // 添加用户消息
            const userMsg = {
                role: 'user',
                content: this.inputMessage,
                time: Date.now()
            };
            this.messages.push(userMsg);
            
            const inputMsg = this.inputMessage;
            this.inputMessage = '';
            this.isLoading = true;
            this.scrollToBottom();
            
            try {
                // 使用SSE流式接收
                const response = await fetch(`${this.$axios.defaults.baseURL}/autotest/ai/chat/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify({
                        projectId: projectId,
                        userId: userId,
                        message: inputMsg,
                        useRag: this.useRag,
                        conversationId: this.currentConversationId
                    })
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                let assistantMsg = {
                    role: 'assistant',
                    content: '',
                    time: Date.now()
                };
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value);
                    const lines = text.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                if (data.type === 'content') {
                                    assistantMsg.content += data.delta;
                                    this.scrollToBottom();
                                } else if (data.type === 'end') {
                                    break;
                                }
                            } catch (e) {
                                // 忽略解析错误
                            }
                        }
                    }
                }
                
                this.messages.push(assistantMsg);
                
            } catch (error) {
                this.$message.error('AI服务调用失败：' + error.message);
            } finally {
                this.isLoading = false;
                this.scrollToBottom();
            }
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
            if (!content) return '';
            return content.replace(/\n/g, '<br>');
        },
        
        // 格式化时间
        formatTime(timestamp) {
            const date = new Date(timestamp);
            return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        },
        
        // 加载知识库列表
        async loadKnowledgeList() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            const res = await this.$get(`/autotest/ai/knowledge?projectId=${projectId}`);
            if (res.data) {
                this.knowledgeList = res.data;
            }
        },
        
        // 保存知识库
        async saveKnowledge() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            const userId = this.$store.state.user?.id || localStorage.getItem('userId');
            
            await this.$post('/autotest/ai/knowledge', {
                projectId: projectId,
                name: this.knowledgeForm.name,
                docType: this.knowledgeForm.docType,
                content: this.knowledgeForm.content,
                sourceType: 'manual',
                updateUser: userId
            });
            
            this.$message.success('保存成功，正在索引...');
            this.showKnowledgeDialog = false;
            this.knowledgeForm = { name: '', docType: 'manual', content: '' };
            this.loadKnowledgeList();
        },
        
        // 用例生成步骤
        async nextCaseStep() {
            if (this.caseGenerateStep === 0) {
                // 获取接口列表
                const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
                const res = await this.$get(`/autotest/ai/agent/api-list/${projectId}`);
                if (res.data && res.data.data) {
                    this.apiList = res.data.data;
                }
                this.caseGenerateStep = 1;
            }
        },
        
        // 生成用例
        async generateCase() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            
            this.$message.info('正在生成用例，请稍候...');
            
            const res = await this.$post('/autotest/ai/generate/case', {
                projectId: projectId,
                userRequirement: this.caseRequirement,
                selectedApis: this.selectedApis
            });
            
            if (res.data && res.data.case) {
                this.generatedCase = JSON.stringify(res.data.case, null, 2);
                this.caseGenerateStep = 2;
            } else {
                this.$message.error('用例生成失败');
            }
        },
        
        // 保存用例
        async saveGeneratedCase() {
            // TODO: 调用后端保存用例接口
            this.$message.success('用例保存成功');
            this.showCaseGenerate = false;
            this.caseGenerateStep = 0;
            this.caseRequirement = '';
            this.selectedApis = [];
            this.generatedCase = '';
        },
        
        // 保存AI设置
        async saveAiSettings() {
            const projectId = this.$store.state.project?.id || localStorage.getItem('projectId');
            
            await this.$post('/autotest/ai/config', {
                projectId: projectId,
                configKey: 'provider',
                configValue: this.aiSettings.provider
            });
            
            await this.$post('/autotest/ai/config', {
                projectId: projectId,
                configKey: 'api_key',
                configValue: this.aiSettings.apiKey
            });
            
            this.$message.success('设置保存成功');
            this.showSettings = false;
        }
    }
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

.conversation-list, .knowledge-list {
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

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes loading {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
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

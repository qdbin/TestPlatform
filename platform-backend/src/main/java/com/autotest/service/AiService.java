package com.autotest.service;

import com.alibaba.fastjson.JSON;
import com.autotest.domain.AiKnowledge;
import com.autotest.domain.AiConversation;
import com.autotest.domain.AiConfig;
import com.autotest.domain.AiApiIndex;
import com.autotest.mapper.AiKnowledgeMapper;
import com.autotest.mapper.AiConversationMapper;
import com.autotest.mapper.AiConfigMapper;
import com.autotest.mapper.AiApiIndexMapper;
import com.autotest.mapper.ApiMapper;
import com.autotest.request.AiKnowledgeRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import javax.annotation.Resource;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service：AI业务逻辑处理
 * 职责：协调AI服务和数据持久化，提供知识库、会话、配置管理
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class AiService {

    @Resource
    private AiKnowledgeMapper aiKnowledgeMapper;

    @Resource
    private AiConversationMapper aiConversationMapper;

    @Resource
    private AiConfigMapper aiConfigMapper;

    @Resource
    private AiApiIndexMapper aiApiIndexMapper;

    @Resource
    private ApiMapper apiMapper;

    @Resource
    private RestTemplate restTemplate;

    // AI服务地址配置
    private static final String AI_SERVICE_URL = "http://localhost:8001";

    // ==================== 知识库管理 ====================

    /**
     * 一、保存知识库文档
     */
    public String saveKnowledge(AiKnowledgeRequest request) {
        AiKnowledge knowledge = new AiKnowledge();
        if (request.getId() == null || request.getId().isEmpty()) {
            knowledge.setId(UUID.randomUUID().toString());
            knowledge.setCreateTime(System.currentTimeMillis());
            knowledge.setCreateUser(request.getUpdateUser());
            knowledge.setStatus("active");
            aiKnowledgeMapper.addKnowledge(knowledge);
        } else {
            knowledge.setId(request.getId());
            knowledge.setUpdateTime(System.currentTimeMillis());
            knowledge.setUpdateUser(request.getUpdateUser());
            aiKnowledgeMapper.updateKnowledge(knowledge);
        }
        knowledge.setProjectId(request.getProjectId());
        knowledge.setName(request.getName());
        knowledge.setContent(request.getContent());
        knowledge.setDocType(request.getDocType() != null ? request.getDocType() : "manual");
        knowledge.setSourceType(request.getSourceType() != null ? request.getSourceType() : "manual");
        knowledge.setUpdateTime(System.currentTimeMillis());
        aiKnowledgeMapper.updateKnowledge(knowledge);
        return knowledge.getId();
    }

    /**
     * 二、删除知识库文档
     */
    public void deleteKnowledge(String knowledgeId) {
        aiKnowledgeMapper.deleteKnowledge(knowledgeId);
    }

    /**
     * 三、获取知识库列表
     */
    public List<AiKnowledge> getKnowledgeList(String projectId) {
        return aiKnowledgeMapper.getKnowledgeList(projectId);
    }

    /**
     * 四、获取知识库详情
     */
    public AiKnowledge getKnowledgeDetail(String knowledgeId) {
        return aiKnowledgeMapper.getKnowledgeById(knowledgeId);
    }

    /**
     * 五、触发知识库索引
     */
    public void indexKnowledge(String knowledgeId) {
        AiKnowledge knowledge = aiKnowledgeMapper.getKnowledgeById(knowledgeId);
        if (knowledge == null) {
            throw new RuntimeException("知识库文档不存在");
        }
        // 调用FastAPI服务进行索引
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("knowledge_id", knowledge.getId());
            params.put("project_id", knowledge.getProjectId());
            params.put("content", knowledge.getContent());
            params.put("name", knowledge.getName());
            restTemplate.postForObject(AI_SERVICE_URL + "/ai/knowledge/index", params, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("知识库索引失败: " + e.getMessage());
        }
    }

    // ==================== 会话管理 ====================

    /**
     * 六、获取会话列表
     */
    public List<AiConversation> getConversationList(String projectId, String userId) {
        return aiConversationMapper.getConversationList(projectId, userId);
    }

    /**
     * 七、获取会话详情
     */
    public AiConversation getConversationDetail(String conversationId) {
        return aiConversationMapper.getConversationById(conversationId);
    }

    /**
     * 八、保存会话消息
     */
    public void saveConversationMessage(String conversationId, String role, String content) {
        AiConversation conversation = aiConversationMapper.getConversationById(conversationId);
        if (conversation == null) {
            throw new RuntimeException("会话不存在");
        }
        List<Map<String, Object>> messages = conversation.getMessages() != null
                ? JSON.parseArray(conversation.getMessages(), Map.class)
                : new ArrayList<>();
        Map<String, Object> message = new HashMap<>();
        message.put("role", role);
        message.put("content", content);
        message.put("time", System.currentTimeMillis());
        messages.add(message);
        conversation.setMessages(JSON.toJSONString(messages));
        conversation.setUpdateTime(System.currentTimeMillis());
        aiConversationMapper.updateConversation(conversation);
    }

    /**
     * 九、创建新会话
     */
    public String createConversation(String projectId, String userId, String sessionType, Boolean useRag) {
        AiConversation conversation = new AiConversation();
        conversation.setId(UUID.randomUUID().toString());
        conversation.setProjectId(projectId);
        conversation.setUserId(userId);
        conversation.setSessionType(sessionType != null ? sessionType : "chat");
        conversation.setTitle("新会话");
        conversation.setMessages("[]");
        conversation.setContext("{}");
        conversation.setUseRag(useRag != null ? (useRag ? 1 : 0) : 1);
        conversation.setStatus("active");
        conversation.setCreateTime(System.currentTimeMillis());
        conversation.setUpdateTime(System.currentTimeMillis());
        aiConversationMapper.addConversation(conversation);
        return conversation.getId();
    }

    /**
     * 十、删除会话
     */
    public void deleteConversation(String conversationId) {
        aiConversationMapper.deleteConversation(conversationId);
    }

    // ==================== 接口同步 ====================

    /**
     * 十一、同步项目接口到知识库
     */
    public void syncProjectApis(String projectId) {
        // 获取项目所有接口
        com.autotest.request.QueryRequest request = new com.autotest.request.QueryRequest();
        request.setProjectId(projectId);
        List<com.autotest.dto.ApiDTO> apis = apiMapper.getApiList(request);
        for (com.autotest.dto.ApiDTO api : apis) {
            String apiId = api.getId();
            // 检查是否已存在
            AiApiIndex existingIndex = aiApiIndexMapper.getApiIndexByApiId(projectId, apiId);
            if (existingIndex != null) {
                continue;
            }
            // 创建索引记录
            AiApiIndex apiIndex = new AiApiIndex();
            apiIndex.setId(UUID.randomUUID().toString());
            apiIndex.setProjectId(projectId);
            apiIndex.setApiId(apiId);
            apiIndex.setApiName(api.getName());
            apiIndex.setApiPath(api.getPath());
            apiIndex.setApiMethod(api.getMethod());
            apiIndex.setApiInfo(com.alibaba.fastjson.JSON.toJSONString(api));
            apiIndex.setIndexedStatus("pending");
            apiIndex.setCreateTime(System.currentTimeMillis());
            apiIndex.setUpdateTime(System.currentTimeMillis());
            aiApiIndexMapper.addApiIndex(apiIndex);
        }
    }

    // ==================== 配置管理 ====================

    /**
     * 十二、获取AI配置
     */
    public Map<String, String> getAiConfig(String projectId) {
        Map<String, String> config = new HashMap<>();
        // 获取全局配置
        List<AiConfig> globalConfigs = aiConfigMapper.getGlobalConfig();
        for (AiConfig c : globalConfigs) {
            config.put(c.getConfigKey(), c.getConfigValue());
        }
        // 获取项目配置（覆盖全局）
        List<AiConfig> projectConfigs = aiConfigMapper.getConfigList(projectId);
        for (AiConfig c : projectConfigs) {
            config.put(c.getConfigKey(), c.getConfigValue());
        }
        return config;
    }

    /**
     * 十三、保存AI配置
     */
    public void saveAiConfig(String projectId, String configKey, String configValue) {
        AiConfig existing = aiConfigMapper.getConfigByKey(configKey, projectId);
        long now = System.currentTimeMillis();
        if (existing == null) {
            AiConfig config = new AiConfig();
            config.setId(UUID.randomUUID().toString());
            config.setConfigKey(configKey);
            config.setConfigValue(configValue);
            config.setIsGlobal(0);
            config.setProjectId(projectId);
            config.setStatus("active");
            config.setCreateTime(now);
            config.setUpdateTime(now);
            aiConfigMapper.addConfig(config);
        } else {
            existing.setConfigValue(configValue);
            existing.setUpdateTime(now);
            aiConfigMapper.updateConfig(existing);
        }
    }

    // ==================== AI对话和用例生成（转发到FastAPI） ====================

    /**
     * 十四、AI对话（SSE流式）
     */
    public Map<String, Object> chat(Map<String, Object> request) {
        try {
            return restTemplate.postForObject(AI_SERVICE_URL + "/ai/chat", request, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("AI服务调用失败: " + e.getMessage());
        }
    }

    /**
     * 十五、用例生成
     */
    public Map<String, Object> generateCase(Map<String, Object> request) {
        try {
            return restTemplate.postForObject(AI_SERVICE_URL + "/ai/agent/generate-case", request, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("用例生成失败: " + e.getMessage());
        }
    }
}

package com.autotest.service;

import com.autotest.domain.AiKnowledge;
import com.autotest.mapper.AiKnowledgeMapper;
import com.autotest.mapper.ApiMapper;
import com.autotest.request.AiKnowledgeRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;

import javax.annotation.Resource;
import java.util.*;

/**
 * Service：AI业务逻辑处理
 * 职责：协调AI服务和数据持久化，提供知识库管理
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class AiService {

    @Resource
    private AiKnowledgeMapper aiKnowledgeMapper;

    @Resource
    private RestTemplate restTemplate;

    // AI服务地址配置
    private static final String AI_SERVICE_URL = "http://localhost:8001";

    private <T> T postToAiService(String path, Object body, String token, Class<T> responseType) {
        HttpHeaders headers = new HttpHeaders();
        if (token != null && !token.isEmpty()) {
            headers.add("token", token);
        }
        HttpEntity<Object> entity = new HttpEntity<>(body, headers);
        ResponseEntity<T> response = restTemplate.exchange(
                AI_SERVICE_URL + path,
                HttpMethod.POST,
                entity,
                responseType);
        return response.getBody();
    }

    private <T> T getFromAiService(String path, String token, Class<T> responseType) {
        HttpHeaders headers = new HttpHeaders();
        if (token != null && !token.isEmpty()) {
            headers.add("token", token);
        }
        HttpEntity<Void> entity = new HttpEntity<>(headers);
        ResponseEntity<T> response = restTemplate.exchange(
                AI_SERVICE_URL + path,
                HttpMethod.GET,
                entity,
                responseType);
        return response.getBody();
    }

    // ==================== 知识库管理 ====================

    /**
     * 一、保存知识库文档
     */
    public String saveKnowledge(AiKnowledgeRequest request) {
        AiKnowledge knowledge = new AiKnowledge();
        boolean isCreate = request.getId() == null || request.getId().isEmpty();
        knowledge.setId(isCreate ? UUID.randomUUID().toString().replace("-", "") : request.getId());
        knowledge.setProjectId(request.getProjectId());
        knowledge.setName(request.getName());
        knowledge.setContent(request.getContent());
        knowledge.setDocType(request.getDocType() != null ? request.getDocType() : "manual");
        knowledge.setSourceType(request.getSourceType() != null ? request.getSourceType() : "manual");
        knowledge.setUpdateTime(System.currentTimeMillis());
        knowledge.setUpdateUser(request.getUpdateUser());

        if (isCreate) {
            knowledge.setCreateTime(System.currentTimeMillis());
            knowledge.setCreateUser(request.getUpdateUser());
            knowledge.setStatus("active");
            aiKnowledgeMapper.addKnowledge(knowledge);
        } else {
            aiKnowledgeMapper.updateKnowledge(knowledge);
        }
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
            postToAiService("/ai/knowledge/index", params, null, Map.class);

            AiKnowledge update = new AiKnowledge();
            update.setId(knowledge.getId());
            update.setName(knowledge.getName());
            update.setContent(knowledge.getContent());
            update.setDocType(knowledge.getDocType());
            update.setSourceType(knowledge.getSourceType());
            update.setStatus("indexed");
            update.setUpdateTime(System.currentTimeMillis());
            update.setUpdateUser(knowledge.getUpdateUser());
            aiKnowledgeMapper.updateKnowledge(update);
        } catch (Exception e) {
            AiKnowledge update = new AiKnowledge();
            update.setId(knowledge.getId());
            update.setName(knowledge.getName());
            update.setContent(knowledge.getContent());
            update.setDocType(knowledge.getDocType());
            update.setSourceType(knowledge.getSourceType());
            update.setStatus("error");
            update.setUpdateTime(System.currentTimeMillis());
            update.setUpdateUser(knowledge.getUpdateUser());
            aiKnowledgeMapper.updateKnowledge(update);
            throw new RuntimeException("知识库索引失败: " + e.getMessage());
        }
    }

    // ==================== AI对话和用例生成（转发到FastAPI） ====================

    /**
     * 十四、AI对话（SSE流式）
     */
    public Map<String, Object> chat(Map<String, Object> request, String token) {
        try {
            return postToAiService("/ai/chat", request, token, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("AI服务调用失败: " + e.getMessage());
        }
    }

    /**
     * 十五、用例生成
     */
    public Map<String, Object> generateCase(Map<String, Object> request, String token) {
        try {
            return postToAiService("/ai/agent/generate-case", request, token, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("用例生成失败: " + e.getMessage());
        }
    }

    public Map<String, Object> getAgentApiList(String projectId, String token) {
        try {
            return getFromAiService("/ai/agent/api-list/" + projectId, token, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("获取接口列表失败: " + e.getMessage());
        }
    }
}

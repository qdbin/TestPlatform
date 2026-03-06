package com.autotest.service;

import com.autotest.domain.AiKnowledge;
import com.autotest.common.exception.LMException;
import com.autotest.dto.ApiDTO;
import com.autotest.mapper.AiKnowledgeMapper;
import com.autotest.mapper.ApiMapper;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.request.CaseApiRequest;
import com.autotest.request.CaseRequest;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
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

    @Resource
    private ObjectMapper objectMapper;

    @Resource
    private ApiMapper apiMapper;

    @Value("${ai.service.base-url:http://localhost:8001}")
    private String aiServiceBaseUrl;

    private <T> T postToAiService(String path, Object body, String token, Class<T> responseType) {
        HttpHeaders headers = new HttpHeaders();
        if (token != null && !token.isEmpty()) {
            headers.add("token", token);
        }
        HttpEntity<Object> entity = new HttpEntity<>(body, headers);
        ResponseEntity<T> response = restTemplate.exchange(
                aiServiceBaseUrl + path,
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
                aiServiceBaseUrl + path,
                HttpMethod.GET,
                entity,
                responseType);
        return response.getBody();
    }

    private void deleteFromAiService(String path) {
        restTemplate.exchange(aiServiceBaseUrl + path, HttpMethod.DELETE, null, Map.class);
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
        knowledge.setParentId(
                request.getParentId() == null || request.getParentId().isEmpty() ? "0" : request.getParentId());
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
            AiKnowledge existed = aiKnowledgeMapper.getKnowledgeById(knowledge.getId());
            if (existed == null) {
                throw new LMException("知识库文档不存在");
            }
            knowledge.setStatus(existed.getStatus() == null ? "active" : existed.getStatus());
            aiKnowledgeMapper.updateKnowledge(knowledge);
        }
        return knowledge.getId();
    }

    /**
     * 二、删除知识库文档
     */
    public void deleteKnowledge(String knowledgeId, String projectId) {
        AiKnowledge knowledge = aiKnowledgeMapper.getKnowledgeById(knowledgeId);
        if (knowledge != null && "folder".equals(knowledge.getDocType())) {
            Integer childCount = aiKnowledgeMapper.countChildren(knowledge.getProjectId(), knowledge.getId());
            if (childCount != null && childCount > 0) {
                throw new LMException("该目录下还有子节点，无法删除");
            }
        }
        String targetProjectId = projectId;
        if (knowledge != null && knowledge.getProjectId() != null && !knowledge.getProjectId().isEmpty()) {
            targetProjectId = knowledge.getProjectId();
        }
        Map<String, Object> deleteRequest = new HashMap<>();
        deleteRequest.put("project_id", targetProjectId);
        deleteRequest.put("doc_id", knowledgeId);
        postToAiService("/ai/rag/delete", deleteRequest, null, Map.class);
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
    public String indexKnowledge(String knowledgeId) {
        AiKnowledge knowledge = aiKnowledgeMapper.getKnowledgeById(knowledgeId);
        if (knowledge == null) {
            throw new LMException("知识库文档不存在");
        }
        if ("folder".equals(knowledge.getDocType())) {
            throw new LMException("目录不支持索引");
        }
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("doc_id", knowledge.getId());
            params.put("project_id", knowledge.getProjectId());
            params.put("doc_type", knowledge.getDocType());
            params.put("doc_name", knowledge.getName());
            params.put("content", knowledge.getContent());
            Map<String, Object> indexResult = postToAiService("/ai/rag/add", params, null, Map.class);
            boolean indexed = indexResult != null && Boolean.TRUE.equals(indexResult.get("indexed"));
            boolean degraded = indexResult != null && Boolean.TRUE.equals(indexResult.get("degraded"));

            AiKnowledge update = new AiKnowledge();
            update.setId(knowledge.getId());
            update.setParentId(knowledge.getParentId());
            update.setName(knowledge.getName());
            update.setContent(knowledge.getContent());
            update.setDocType(knowledge.getDocType());
            update.setSourceType(knowledge.getSourceType());
            if (indexed) {
                update.setStatus("indexed");
            } else if (degraded) {
                update.setStatus("degraded");
            } else {
                update.setStatus("error");
            }
            update.setUpdateTime(System.currentTimeMillis());
            update.setUpdateUser(knowledge.getUpdateUser());
            aiKnowledgeMapper.updateKnowledge(update);
            if (!indexed && !degraded) {
                String error = indexResult == null ? "未知错误" : String.valueOf(indexResult.getOrDefault("error", "索引失败"));
                throw new LMException("知识库索引失败: " + error);
            }
            return update.getStatus();
        } catch (Exception e) {
            AiKnowledge update = new AiKnowledge();
            update.setId(knowledge.getId());
            update.setParentId(knowledge.getParentId());
            update.setName(knowledge.getName());
            update.setContent(knowledge.getContent());
            update.setDocType(knowledge.getDocType());
            update.setSourceType(knowledge.getSourceType());
            update.setStatus("error");
            update.setUpdateTime(System.currentTimeMillis());
            update.setUpdateUser(knowledge.getUpdateUser());
            aiKnowledgeMapper.updateKnowledge(update);
            throw new LMException("知识库索引失败: " + e.getMessage());
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
            throw new LMException("AI服务调用失败: " + e.getMessage());
        }
    }

    public void streamChat(Map<String, Object> request, String token, SseEmitter emitter) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (token != null && !token.isEmpty()) {
            headers.add("token", token);
        }
        HttpEntity<Object> entity = new HttpEntity<>(request, headers);

        try {
            restTemplate.execute(
                aiServiceBaseUrl + "/ai/chat/stream",
                    HttpMethod.POST,
                    restTemplate.httpEntityCallback(entity),
                    response -> {
                        try (BufferedReader reader = new BufferedReader(
                                new InputStreamReader(response.getBody(), StandardCharsets.UTF_8))) {
                            String line;
                            while ((line = reader.readLine()) != null) {
                                if (!line.startsWith("data:")) {
                                    continue;
                                }
                                String payload = line.replaceFirst("^data:\\s*", "").trim();
                                if (payload.isEmpty()) {
                                    continue;
                                }
                                Map<String, Object> event = objectMapper.readValue(
                                        payload,
                                        new TypeReference<Map<String, Object>>() {
                                        });
                                emitter.send(SseEmitter.event().data(event));
                                if ("end".equals(String.valueOf(event.get("type")))) {
                                    break;
                                }
                            }
                        }
                        return null;
                    });
            emitter.complete();
        } catch (Exception e) {
            try {
                Map<String, Object> errorPayload = new HashMap<>();
                errorPayload.put("type", "error");
                errorPayload.put("message", "AI服务调用失败: " + e.getMessage());
                emitter.send(SseEmitter.event().data(errorPayload));
            } catch (Exception ignored) {
            }
            emitter.complete();
        }
    }

    /**
     * 十五、用例生成
     */
    public Map<String, Object> generateCase(Map<String, Object> request, String token) {
        try {
            return postToAiService("/ai/agent/generate-case", request, token, Map.class);
        } catch (Exception e) {
            throw new LMException("用例生成失败: " + e.getMessage());
        }
    }

    public Map<String, Object> getAgentApiList(String projectId, String token) {
        try {
            return getFromAiService("/ai/agent/api-list/" + projectId, token, Map.class);
        } catch (Exception e) {
            throw new LMException("获取接口列表失败: " + e.getMessage());
        }
    }

    public void validateCaseApiIds(String projectId, CaseRequest caseRequest) {
        if (caseRequest == null || caseRequest.getCaseApis() == null || caseRequest.getCaseApis().isEmpty()) {
            throw new LMException("用例步骤不能为空");
        }
        for (CaseApiRequest step : caseRequest.getCaseApis()) {
            if (step == null || step.getApiId() == null || step.getApiId().trim().isEmpty()) {
                throw new LMException("用例步骤必须包含apiId");
            }
            ApiDTO api = apiMapper.getApiDetail(step.getApiId());
            if (api == null || api.getProjectId() == null || !projectId.equals(api.getProjectId())) {
                throw new LMException("用例步骤包含无效接口，请先创建接口");
            }
        }
    }
}

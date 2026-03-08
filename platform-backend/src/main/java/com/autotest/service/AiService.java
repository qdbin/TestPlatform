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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
    private static final Logger log = LoggerFactory.getLogger(AiService.class);

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
            // 索引请求Schema示例：
            // {"doc_id":"d1","project_id":"p1","doc_type":"manual","doc_name":"登录规范","content":"..."}
            Map<String, Object> params = new HashMap<>();
            params.put("doc_id", knowledge.getId());
            params.put("project_id", knowledge.getProjectId());
            params.put("doc_type", knowledge.getDocType());
            params.put("doc_name", knowledge.getName());
            params.put("content", knowledge.getContent());
            Map<String, Object> indexResult = postToAiService("/ai/rag/add", params, null, Map.class);
            boolean indexed = indexResult != null && Boolean.TRUE.equals(indexResult.get("indexed"));
            boolean degraded = indexResult != null && Boolean.TRUE.equals(indexResult.get("degraded"));
            String indexError = indexResult == null ? "" : String.valueOf(indexResult.getOrDefault("error", ""));
            if (indexed && "fallback_embedding".equals(indexError)) {
                // AI侧使用降级向量时，业务可用但质量下降，标记为degraded以便前端提示。
                degraded = true;
            }

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

    /**
     * 流式对话转发：
     * 读取AI服务SSE事件并原样转发给前端，维持 content/case/error/end 事件协议。
     */
    public void streamChat(Map<String, Object> request, String token, SseEmitter emitter) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (token != null && !token.isEmpty()) {
            headers.add("token", token);
        }
        HttpEntity<Object> entity = new HttpEntity<>(request, headers);
        long streamStart = System.currentTimeMillis();
        final long[] firstEventAt = { 0L };
        final int[] eventCount = { 0 };

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
                                // 仅处理SSE数据行，忽略注释/空行。
                                if (!line.startsWith("data:")) {
                                    continue;
                                }
                                String payload = line.replaceFirst("^data:\\s*", "").trim();
                                if (payload.isEmpty()) {
                                    continue;
                                }
                                // 每个data块按JSON事件解析，保持事件边界不被重组。
                                Map<String, Object> event = objectMapper.readValue(
                                        payload,
                                        new TypeReference<Map<String, Object>>() {
                                        });
                                long now = System.currentTimeMillis();
                                eventCount[0] += 1;
                                if (firstEventAt[0] == 0L) {
                                    firstEventAt[0] = now;
                                    log.info("AI流式首包到达 delay={}ms", firstEventAt[0] - streamStart);
                                }
                                if (eventCount[0] % 20 == 0 || "end".equals(String.valueOf(event.get("type")))) {
                                    log.info("AI流式转发进度 events={} elapsed={}ms type={}",
                                            eventCount[0], now - streamStart, String.valueOf(event.get("type")));
                                }
                                // 直通发送给前端，避免后端层再做拼接缓存。
                                emitter.send(SseEmitter.event().data(event));
                                if ("end".equals(String.valueOf(event.get("type")))) {
                                    break;
                                }
                            }
                        }
                        return null;
                    });
            log.info("AI流式转发完成 events={} total={}ms", eventCount[0], System.currentTimeMillis() - streamStart);
            emitter.complete();
        } catch (Exception e) {
            log.error("AI流式转发失败 total={}ms error={}", System.currentTimeMillis() - streamStart, e.getMessage(), e);
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

    /**
     * Agent调度辅助接口。
     * 将项目接口列表透传给ai-service，供其进行接口选择与链路编排。
     */
    public Map<String, Object> getAgentApiList(String projectId, String token) {
        try {
            return getFromAiService("/ai/agent/api-list/" + projectId, token, Map.class);
        } catch (Exception e) {
            throw new LMException("获取接口列表失败: " + e.getMessage());
        }
    }

    /**
     * 保存AI草稿前校验步骤引用的apiId必须属于当前项目。
     */
    public void validateCaseApiIds(String projectId, CaseRequest caseRequest) {
        if (caseRequest == null || caseRequest.getCaseApis() == null || caseRequest.getCaseApis().isEmpty()) {
            throw new LMException("请先创建接口");
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

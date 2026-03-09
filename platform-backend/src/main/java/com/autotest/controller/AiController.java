package com.autotest.controller;

import com.autotest.common.exception.LMException;
import com.autotest.domain.AiKnowledge;
import com.autotest.request.AiChatStreamRequest;
import com.autotest.request.AiGenerateCaseRequest;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.service.AiService;
import com.autotest.service.ai.AiPermissionService;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.*;
import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/autotest/ai")
public class AiController {

    @Resource
    private AiService aiService;

    @Resource
    private AiPermissionService aiPermissionService;

    @Resource(name = "aiStreamTaskExecutor")
    private TaskExecutor aiStreamTaskExecutor;

    @GetMapping("/knowledge")
    public List<Map<String, Object>> getKnowledgeList(@RequestParam String projectId, HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        String userId = aiPermissionService.getLoginUserId(request);
        boolean canManageAll = aiPermissionService.canManageKnowledge(request, projectId);
        List<AiKnowledge> list = aiService.getKnowledgeList(projectId);
        List<Map<String, Object>> result = new ArrayList<>();
        for (AiKnowledge knowledge : list) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", knowledge.getId());
            item.put("projectId", knowledge.getProjectId());
            item.put("parentId", knowledge.getParentId());
            item.put("name", knowledge.getName());
            item.put("docType", knowledge.getDocType());
            item.put("sourceType", knowledge.getSourceType());
            item.put("status", knowledge.getStatus());
            item.put("indexedStatus", mapIndexedStatus(knowledge.getStatus()));
            item.put("createTime", knowledge.getCreateTime());
            item.put("updateTime", knowledge.getUpdateTime());
            item.put("createUser", knowledge.getCreateUser());
            item.put("canEdit", canManageAll || userId.equals(knowledge.getCreateUser()));
            result.add(item);
        }
        return result;
    }

    @GetMapping("/knowledge/{id}")
    public Map<String, Object> getKnowledgeDetail(@PathVariable String id, @RequestParam String projectId,
            HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        AiKnowledge knowledge = aiService.getKnowledgeDetail(id);
        if (knowledge == null || !projectId.equals(knowledge.getProjectId())) {
            throw new LMException("知识库文档不存在");
        }
        boolean canManageAll = aiPermissionService.canManageKnowledge(request, projectId);
        String userId = aiPermissionService.getLoginUserId(request);
        Map<String, Object> detail = new HashMap<>();
        detail.put("id", knowledge.getId());
        detail.put("projectId", knowledge.getProjectId());
        detail.put("parentId", knowledge.getParentId());
        detail.put("name", knowledge.getName());
        detail.put("content", knowledge.getContent());
        detail.put("docType", knowledge.getDocType());
        detail.put("sourceType", knowledge.getSourceType());
        detail.put("status", knowledge.getStatus());
        detail.put("createTime", knowledge.getCreateTime());
        detail.put("updateTime", knowledge.getUpdateTime());
        detail.put("createUser", knowledge.getCreateUser());
        detail.put("updateUser", knowledge.getUpdateUser());
        detail.put("canEdit", canManageAll || userId.equals(knowledge.getCreateUser()));
        return detail;
    }

    @PostMapping("/knowledge")
    public String saveKnowledge(@RequestBody AiKnowledgeRequest request, HttpServletRequest httpRequest) {
        aiPermissionService.assertProjectAccess(httpRequest, request.getProjectId());
        String loginUserId = aiPermissionService.getLoginUserId(httpRequest);
        request.setUpdateUser(loginUserId);
        if (request.getId() != null && !request.getId().isEmpty()) {
            AiKnowledge existed = aiService.getKnowledgeDetail(request.getId());
            if (!aiPermissionService.canManageKnowledgeItem(httpRequest, existed)) {
                throw new LMException("无权限操作知识库");
            }
        } else if (loginUserId.isEmpty()) {
            throw new LMException("未登录");
        }
        return aiService.saveKnowledge(request);
    }

    @DeleteMapping("/knowledge/{id}")
    public String deleteKnowledge(@PathVariable String id, @RequestParam String projectId, HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        AiKnowledge existed = aiService.getKnowledgeDetail(id);
        if (!aiPermissionService.canManageKnowledgeItem(request, existed)) {
            throw new LMException("无权限操作知识库");
        }
        aiService.deleteKnowledge(id, projectId);
        return "删除成功";
    }

    @PostMapping("/knowledge/index/{id}")
    public Map<String, String> indexKnowledge(@PathVariable String id, @RequestParam String projectId,
            HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        AiKnowledge existed = aiService.getKnowledgeDetail(id);
        if (!aiPermissionService.canManageKnowledgeItem(request, existed)) {
            throw new LMException("无权限操作知识库");
        }
        String status = aiService.indexKnowledge(id);
        Map<String, String> result = new HashMap<>();
        result.put("msg", "索引完成");
        result.put("indexedStatus", "indexed".equals(status) ? "ready" : status);
        return result;
    }

    @PostMapping("/generate-case")
    public Map<String, Object> generateCase(@RequestBody AiGenerateCaseRequest request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpRequest) {
        aiPermissionService.assertProjectAccess(httpRequest, request.getProjectId());
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", request.getProjectId());
        payload.put("user_requirement", request.getUserRequirement());
        payload.put("selected_apis", request.getSelectedApis() == null ? new ArrayList<>() : request.getSelectedApis());
        payload.put("messages", request.getMessages() == null ? new ArrayList<>() : request.getMessages());
        return aiService.generateCase(payload, token);
    }

    @GetMapping("/agent/api-list/{projectId}")
    public Map<String, Object> getAgentApiList(@PathVariable String projectId,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        return aiService.getAgentApiList(projectId, token);
    }

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@RequestBody AiChatStreamRequest request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpRequest,
            HttpServletResponse response) {
        aiPermissionService.assertProjectAccess(httpRequest, request.getProjectId());
        response.setHeader("Cache-Control", "no-cache");
        response.setHeader("Connection", "keep-alive");
        response.setHeader("X-Accel-Buffering", "no");
        SseEmitter emitter = new SseEmitter(300000L);
        CompletableFuture.runAsync(() -> {
            try {
                aiService.streamChat(buildChatRequest(request), token, emitter);
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
        }, aiStreamTaskExecutor);
        return emitter;
    }

    private Map<String, Object> buildChatRequest(AiChatStreamRequest request) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", request.getProjectId());
        payload.put("message", request.getMessage());
        payload.put("question", request.getMessage());
        payload.put("use_rag", request.getUseRag() == null || request.getUseRag());
        payload.put("messages", request.getMessages() == null ? new ArrayList<>() : request.getMessages());
        return payload;
    }

    private String mapIndexedStatus(String status) {
        if ("indexed".equals(status)) {
            return "ready";
        }
        if ("error".equals(status)) {
            return "error";
        }
        if ("degraded".equals(status)) {
            return "degraded";
        }
        return "pending";
    }
}

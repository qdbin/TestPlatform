package com.autotest.controller;

import com.autotest.domain.AiKnowledge;
import com.autotest.domain.Project;
import com.autotest.common.exception.LMException;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.request.CaseRequest;
import com.autotest.service.AiService;
import com.autotest.service.CaseService;
import com.autotest.service.ProjectService;
import com.autotest.mapper.ProjectMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;

/**
 * Controller：AI智能助手控制器
 * 职责：处理AI对话、知识库管理、用例生成等HTTP请求
 */
@RestController
@RequestMapping("/autotest/ai")
public class AiController {

    @Resource
    private AiService aiService;

    @Resource
    private ProjectService projectService;

    @Resource
    private ProjectMapper projectMapper;

    @Resource
    private CaseService caseService;

    @Resource
    private ObjectMapper objectMapper;

    private String getLoginUserId(HttpServletRequest request) {
        Object userId = request.getSession(true).getAttribute("userId");
        return userId != null ? userId.toString() : "";
    }

    private boolean isSuperAdmin(String userId) {
        return "system_admin_user".equals(userId);
    }

    private Project assertProjectAccess(HttpServletRequest request, String projectId) {
        if (projectId == null || projectId.isEmpty()) {
            throw new LMException("projectId不能为空");
        }
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            throw new LMException("未登录");
        }
        if (isSuperAdmin(userId)) {
            Project project = projectService.getProjectInfo(projectId);
            if (project == null) {
                throw new LMException("项目不存在");
            }
            return project;
        }

        Project project = projectService.getProjectInfo(projectId);
        if (project == null) {
            throw new LMException("项目不存在");
        }

        if (projectMapper.getProjectUser(projectId, userId) == null) {
            throw new LMException("无项目权限");
        }
        return project;
    }

    private boolean canManageKnowledge(HttpServletRequest request, String projectId) {
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            return false;
        }
        if (isSuperAdmin(userId)) {
            return true;
        }
        Project project = projectService.getProjectInfo(projectId);
        if (project == null) {
            return false;
        }
        return userId.equals(project.getProjectAdmin());
    }

    private boolean canManageKnowledgeItem(HttpServletRequest request, AiKnowledge knowledge) {
        if (knowledge == null) {
            return false;
        }
        String userId = getLoginUserId(request);
        if (userId.isEmpty()) {
            return false;
        }
        if (isSuperAdmin(userId)) {
            return true;
        }
        Project project = projectService.getProjectInfo(knowledge.getProjectId());
        if (project != null && userId.equals(project.getProjectAdmin())) {
            return true;
        }
        return userId.equals(knowledge.getCreateUser());
    }

    // ==================== 知识库管理 ====================

    /**
     * 一、获取知识库列表
     */
    @GetMapping("/knowledge")
    public Map<String, Object> getKnowledgeList(@RequestParam String projectId, HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        String userId = getLoginUserId(httpServletRequest);
        Project project = projectService.getProjectInfo(projectId);
        boolean canManageAll = canManageKnowledge(httpServletRequest, projectId);
        List<Map<String, Object>> safeList = new ArrayList<>();
        List<AiKnowledge> list = aiService.getKnowledgeList(projectId);
        for (AiKnowledge k : list) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", k.getId());
            item.put("projectId", k.getProjectId());
            item.put("parentId", k.getParentId());
            item.put("name", k.getName());
            item.put("docType", k.getDocType());
            item.put("sourceType", k.getSourceType());
            item.put("status", k.getStatus());
            if ("indexed".equals(k.getStatus())) {
                item.put("indexedStatus", "ready");
            } else if ("error".equals(k.getStatus())) {
                item.put("indexedStatus", "error");
            } else if ("degraded".equals(k.getStatus())) {
                item.put("indexedStatus", "degraded");
            } else {
                item.put("indexedStatus", "pending");
            }
            item.put("createTime", k.getCreateTime());
            item.put("updateTime", k.getUpdateTime());
            item.put("createUser", k.getCreateUser());
            boolean canEdit = canManageAll || userId.equals(k.getCreateUser());
            item.put("canEdit", canEdit);
            item.put("isProjectAdmin", project != null && userId.equals(project.getProjectAdmin()));
            safeList.add(item);
        }
        Map<String, Object> result = new HashMap<>();
        result.put("data", safeList);
        return result;
    }

    /**
     * 二、获取知识库详情
     */
    @GetMapping("/knowledge/{id}")
    public Map<String, Object> getKnowledgeDetail(@PathVariable String id, @RequestParam String projectId,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        AiKnowledge knowledge = aiService.getKnowledgeDetail(id);
        if (knowledge == null) {
            throw new LMException("知识库文档不存在");
        }
        if (!projectId.equals(knowledge.getProjectId())) {
            throw new LMException("知识库文档不存在");
        }
        String userId = getLoginUserId(httpServletRequest);
        boolean canManageAll = canManageKnowledge(httpServletRequest, projectId);
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
        Map<String, Object> result = new HashMap<>();
        result.put("data", detail);
        return result;
    }

    /**
     * 三、保存知识库文档
     */
    @PostMapping("/knowledge")
    public Map<String, Object> saveKnowledge(@RequestBody AiKnowledgeRequest request,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, request.getProjectId());
        String loginUserId = getLoginUserId(httpServletRequest);
        request.setUpdateUser(loginUserId);
        if (request.getId() != null && !request.getId().isEmpty()) {
            AiKnowledge existed = aiService.getKnowledgeDetail(request.getId());
            if (!canManageKnowledgeItem(httpServletRequest, existed)) {
                throw new LMException("无权限操作知识库");
            }
        } else if (loginUserId.isEmpty()) {
            throw new LMException("未登录");
        }
        String id = aiService.saveKnowledge(request);
        Map<String, Object> result = new HashMap<>();
        result.put("data", id);
        return result;
    }

    /**
     * 四、删除知识库文档
     */
    @DeleteMapping("/knowledge/{id}")
    public Map<String, Object> deleteKnowledge(@PathVariable String id, @RequestParam String projectId,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        AiKnowledge existed = aiService.getKnowledgeDetail(id);
        if (!canManageKnowledgeItem(httpServletRequest, existed)) {
            throw new LMException("无权限操作知识库");
        }
        aiService.deleteKnowledge(id, projectId);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "删除成功");
        return result;
    }

    /**
     * 五、触发知识库索引
     */
    @PostMapping("/knowledge/index/{id}")
    public Map<String, Object> indexKnowledge(@PathVariable String id, @RequestParam String projectId,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        AiKnowledge existed = aiService.getKnowledgeDetail(id);
        if (!canManageKnowledgeItem(httpServletRequest, existed)) {
            throw new LMException("无权限操作知识库");
        }
        String indexedStatus = aiService.indexKnowledge(id);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "索引完成");
        result.put("indexedStatus", "indexed".equals(indexedStatus) ? "ready" : indexedStatus);
        return result;
    }

    // ==================== AI对话 ====================

    /**
     * 十一、AI对话（SSE流式）
     */
    @PostMapping("/chat/stream")
    public SseEmitter chatStream(@RequestBody Map<String, Object> request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest) {
        String projectId = (String) request.get("projectId");
        assertProjectAccess(httpServletRequest, projectId);
        SseEmitter emitter = new SseEmitter(300000L); // 5分钟超时

        CompletableFuture.runAsync(() -> {
            try {
                String message = (String) request.get("message");
                Boolean useRag = (Boolean) request.getOrDefault("useRag", true);
                String conversationId = (String) request.get("conversationId");

                Map<String, Object> aiRequest = new HashMap<>();
                aiRequest.put("project_id", projectId);
                aiRequest.put("message", message);
                aiRequest.put("use_rag", useRag);
                aiRequest.put("conversation_id", conversationId != null ? conversationId : "");
                aiRequest.put("history_messages", request.get("historyMessages"));
                aiService.streamChat(aiRequest, token, emitter);
            } catch (Exception e) {
                emitter.complete();
            }
        });

        return emitter;
    }

    // ==================== 用例生成 ====================

    /**
     * 十二、生成测试用例
     */
    @PostMapping("/generate/case")
    public Map<String, Object> generateCase(@RequestBody Map<String, Object> request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest) {
        String projectId = request.get("projectId") == null ? null : String.valueOf(request.get("projectId"));
        assertProjectAccess(httpServletRequest, projectId);
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", projectId);
        payload.put("user_requirement", request.get("userRequirement"));
        payload.put("selected_apis", request.get("selectedApis"));
        return aiService.generateCase(payload, token);
    }

    @GetMapping("/agent/api-list/{projectId}")
    public Map<String, Object> getAgentApiList(@PathVariable String projectId,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        return aiService.getAgentApiList(projectId, token);
    }

    /**
     * 十三、保存生成的用例
     */
    @PostMapping("/generate/case/save")
    public Map<String, Object> saveGeneratedCase(@RequestBody Map<String, Object> request,
            HttpServletRequest httpServletRequest) {
        Object caseObj = request.get("case");
        if (!(caseObj instanceof Map)) {
            throw new LMException("case参数不能为空");
        }
        CaseRequest caseRequest = objectMapper.convertValue(caseObj, CaseRequest.class);
        assertProjectAccess(httpServletRequest, caseRequest.getProjectId());
        caseRequest.setUpdateUser(getLoginUserId(httpServletRequest));
        caseService.saveCase(caseRequest);
        Map<String, Object> result = new HashMap<>();
        result.put("data", "success");
        result.put("msg", "用例保存成功");
        return result;
    }

}

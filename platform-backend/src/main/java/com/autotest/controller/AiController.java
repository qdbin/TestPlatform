package com.autotest.controller;

import com.autotest.domain.AiKnowledge;
import com.autotest.domain.Project;
import com.autotest.common.exception.LMException;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.request.AiChatStreamRequest;
import com.autotest.request.AiGenerateCaseRequest;
import com.autotest.request.CaseRequest;
import com.autotest.service.AiService;
import com.autotest.service.CaseService;
import com.autotest.service.ProjectService;
import com.autotest.mapper.ProjectMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.MediaType;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.Arrays;
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

    @Resource
    private RestTemplate restTemplate;

    @Resource(name = "aiStreamTaskExecutor")
    private TaskExecutor aiStreamTaskExecutor;

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
        // 知识文档增改统一入口：create/update通过id是否为空区分。
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
        // 删除前必须做“项目权限 + 文档粒度权限”双重校验。
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
        // 索引触发后由服务层同步更新indexed/degraded/error状态。
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
    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@RequestBody AiChatStreamRequest request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest,
            HttpServletResponse httpServletResponse) {
        String projectId = request.getProjectId();
        assertProjectAccess(httpServletRequest, projectId);
        // 显式声明SSE防缓冲响应头，降低代理层攒包风险。
        httpServletResponse.setHeader("Cache-Control", "no-cache");
        httpServletResponse.setHeader("Connection", "keep-alive");
        httpServletResponse.setHeader("X-Accel-Buffering", "no");
        SseEmitter emitter = new SseEmitter(300000L); // 5分钟超时

        // 使用专用线程池，避免公共线程池拥堵导致首包延迟。
        CompletableFuture.runAsync(() -> {
            try {
                String message = request.getMessage();
                boolean useRag = request.getUseRag() == null || request.getUseRag();

                // 字段映射：前端驼峰字段转AI服务下划线字段。
                Map<String, Object> aiRequest = new HashMap<>();
                aiRequest.put("project_id", projectId);
                aiRequest.put("message", message);
                aiRequest.put("question", message);
                aiRequest.put("use_rag", useRag);
                aiRequest.put("messages", request.getMessages());
                aiService.streamChat(aiRequest, token, emitter);
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

    // ==================== 用例生成 ====================

    /**
     * 十二、生成测试用例
     */
    @PostMapping("/generate/case")
    public Map<String, Object> generateCase(@RequestBody AiGenerateCaseRequest request,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest) {
        String projectId = request.getProjectId();
        assertProjectAccess(httpServletRequest, projectId);
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", projectId);
        payload.put("user_requirement", request.getUserRequirement());
        payload.put("selected_apis", request.getSelectedApis());
        payload.put("messages", request.getMessages());
        return aiService.generateCase(payload, token);
    }

    @GetMapping("/agent/api-list/{projectId}")
    public Map<String, Object> getAgentApiList(@PathVariable String projectId,
            @RequestHeader(value = "token", required = false) String token,
            HttpServletRequest httpServletRequest) {
        /**
         * Agent调度辅助接口：
         * 给前端“选择接口”场景提供当前项目完整接口清单。
         */
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
        if (!"API".equalsIgnoreCase(caseRequest.getType())) {
            throw new LMException("AI生成保存仅支持API用例");
        }
        assertProjectAccess(httpServletRequest, caseRequest.getProjectId());
        aiService.validateCaseApiIds(caseRequest.getProjectId(), caseRequest);
        caseRequest.setUpdateUser(getLoginUserId(httpServletRequest));
        caseService.saveCase(caseRequest);
        Map<String, Object> result = new HashMap<>();
        result.put("data", "success");
        result.put("msg", "用例保存成功");
        return result;
    }

    @GetMapping("/schema/case")
    public Map<String, Object> getCaseSchema(@RequestParam String projectId, HttpServletRequest httpServletRequest) {
        // 仅抽取Case生成所需Schema，减少上下文体积。
        assertProjectAccess(httpServletRequest, projectId);
        return getSchemaByNames(projectId, "CaseRequest,CaseApiRequest", httpServletRequest);
    }

    @GetMapping("/schema/extract")
    public Map<String, Object> getSchemaByNames(@RequestParam String projectId,
            @RequestParam String names,
            HttpServletRequest httpServletRequest) {
        // Schema抽取示例：names=CaseRequest,CaseApiRequest
        assertProjectAccess(httpServletRequest, projectId);
        String contextUrl = httpServletRequest.getScheme() + "://" + httpServletRequest.getServerName() + ":"
                + httpServletRequest.getServerPort();
        Map<String, Object> openapi = restTemplate.getForObject(contextUrl + "/v3/api-docs", Map.class);
        Map<String, Object> result = new HashMap<>();
        Map<String, Object> data = new HashMap<>();
        List<String> targetNames = Arrays.asList(String.valueOf(names).split(","));
        if (openapi != null && openapi.get("components") instanceof Map) {
            Map<?, ?> components = (Map<?, ?>) openapi.get("components");
            if (components.get("schemas") instanceof Map) {
                Map<?, ?> schemas = (Map<?, ?>) components.get("schemas");
                for (String rawName : targetNames) {
                    String name = rawName == null ? "" : rawName.trim();
                    if (name.isEmpty()) {
                        continue;
                    }
                    Object schema = schemas.get(name);
                    if (schema instanceof Map) {
                        data.put(name, schema);
                    }
                }
            }
        }
        result.put("data", data);
        return result;
    }

}

package com.autotest.controller;

import com.autotest.domain.AiKnowledge;
import com.autotest.domain.Project;
import com.autotest.common.exception.LMException;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.service.AiService;
import com.autotest.service.ProjectService;
import com.autotest.mapper.ProjectMapper;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.io.IOException;
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

    // ==================== 知识库管理 ====================

    /**
     * 一、获取知识库列表
     */
    @GetMapping("/knowledge")
    public Map<String, Object> getKnowledgeList(@RequestParam String projectId, HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, projectId);
        boolean canManage = canManageKnowledge(httpServletRequest, projectId);
        List<Map<String, Object>> safeList = new ArrayList<>();
        if (canManage) {
            List<AiKnowledge> list = aiService.getKnowledgeList(projectId);
            for (AiKnowledge k : list) {
                Map<String, Object> item = new HashMap<>();
                item.put("id", k.getId());
                item.put("projectId", k.getProjectId());
                item.put("name", k.getName());
                item.put("docType", k.getDocType());
                item.put("sourceType", k.getSourceType());
                item.put("status", k.getStatus());
                item.put("indexedStatus", "indexed".equals(k.getStatus()) ? "ready" : "pending");
                item.put("createTime", k.getCreateTime());
                item.put("updateTime", k.getUpdateTime());
                safeList.add(item);
            }
        }
        Map<String, Object> result = new HashMap<>();
        result.put("data", safeList);
        return result;
    }

    /**
     * 二、获取知识库详情
     */
    @GetMapping("/knowledge/{id}")
    public Map<String, Object> getKnowledgeDetail(@PathVariable String id) {
        throw new LMException("知识库文档不支持查看内容");
    }

    /**
     * 三、保存知识库文档
     */
    @PostMapping("/knowledge")
    public Map<String, Object> saveKnowledge(@RequestBody AiKnowledgeRequest request,
            HttpServletRequest httpServletRequest) {
        assertProjectAccess(httpServletRequest, request.getProjectId());
        if (!canManageKnowledge(httpServletRequest, request.getProjectId())) {
            throw new LMException("无权限操作知识库");
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
        if (!canManageKnowledge(httpServletRequest, projectId)) {
            throw new LMException("无权限操作知识库");
        }
        aiService.deleteKnowledge(id);
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
        if (!canManageKnowledge(httpServletRequest, projectId)) {
            throw new LMException("无权限操作知识库");
        }
        aiService.indexKnowledge(id);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "索引任务已提交");
        return result;
    }

    // ==================== AI对话 ====================

    /**
     * 十一、AI对话（SSE流式）
     */
    @PostMapping("/chat/stream")
    public SseEmitter chatStream(@RequestBody Map<String, Object> request,
            @RequestHeader(value = "token", required = false) String token) {
        SseEmitter emitter = new SseEmitter(300000L); // 5分钟超时

        CompletableFuture.runAsync(() -> {
            try {
                String projectId = (String) request.get("projectId");
                String message = (String) request.get("message");
                Boolean useRag = (Boolean) request.getOrDefault("useRag", true);
                String conversationId = (String) request.get("conversationId");

                // 构建转发请求
                Map<String, Object> aiRequest = new HashMap<>();
                aiRequest.put("project_id", projectId);
                aiRequest.put("message", message);
                aiRequest.put("use_rag", useRag);
                aiRequest.put("conversation_id", conversationId != null ? conversationId : "");

                // 调用AI服务（简化处理，实际应该使用SSE）
                Map<String, Object> aiResponse = aiService.chat(aiRequest, token);

                // 发送响应
                String content = (String) aiResponse.get("content");
                if (content != null) {
                    Map<String, Object> payload = new HashMap<>();
                    payload.put("type", "content");
                    payload.put("delta", content);
                    emitter.send(SseEmitter.event().data(payload));
                }

                Object caseDraft = aiResponse.get("case");
                if (caseDraft != null) {
                    Map<String, Object> payload = new HashMap<>();
                    payload.put("type", "case");
                    payload.put("case", caseDraft);
                    emitter.send(SseEmitter.event().data(payload));
                }

                // 保存AI响应
                Map<String, Object> endPayload = new HashMap<>();
                endPayload.put("type", "end");
                emitter.send(SseEmitter.event().data(endPayload));
                emitter.complete();

            } catch (Exception e) {
                try {
                    Map<String, Object> errorPayload = new HashMap<>();
                    errorPayload.put("type", "error");
                    errorPayload.put("message", e.getMessage());
                    emitter.send(SseEmitter.event().data(errorPayload));
                } catch (IOException ignore) {
                }
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
            @RequestHeader(value = "token", required = false) String token) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("project_id", request.get("projectId"));
        payload.put("user_requirement", request.get("userRequirement"));
        payload.put("selected_apis", request.get("selectedApis"));
        return aiService.generateCase(payload, token);
    }

    @GetMapping("/agent/api-list/{projectId}")
    public Map<String, Object> getAgentApiList(@PathVariable String projectId,
            @RequestHeader(value = "token", required = false) String token) {
        return aiService.getAgentApiList(projectId, token);
    }

    /**
     * 十三、保存生成的用例
     */
    @PostMapping("/generate/case/save")
    public Map<String, Object> saveGeneratedCase(@RequestBody Map<String, Object> request) {
        // TODO: 调用CaseService保存用例
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "用例保存成功");
        return result;
    }

}

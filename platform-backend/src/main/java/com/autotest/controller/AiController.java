package com.autotest.controller;

import com.autotest.domain.AiKnowledge;
import com.autotest.domain.AiConversation;
import com.autotest.domain.AiConfig;
import com.autotest.request.AiKnowledgeRequest;
import com.autotest.service.AiService;
import com.autotest.service.UserService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
    private UserService userService;

    // ==================== 知识库管理 ====================

    /**
     * 一、获取知识库列表
     */
    @GetMapping("/knowledge")
    public Map<String, Object> getKnowledgeList(@RequestParam String projectId) {
        List<AiKnowledge> list = aiService.getKnowledgeList(projectId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        return result;
    }

    /**
     * 二、获取知识库详情
     */
    @GetMapping("/knowledge/{id}")
    public Map<String, Object> getKnowledgeDetail(@PathVariable String id) {
        AiKnowledge knowledge = aiService.getKnowledgeDetail(id);
        Map<String, Object> result = new HashMap<>();
        result.put("data", knowledge);
        return result;
    }

    /**
     * 三、保存知识库文档
     */
    @PostMapping("/knowledge")
    public Map<String, Object> saveKnowledge(@RequestBody AiKnowledgeRequest request) {
        String id = aiService.saveKnowledge(request);
        Map<String, Object> result = new HashMap<>();
        result.put("data", id);
        return result;
    }

    /**
     * 四、删除知识库文档
     */
    @DeleteMapping("/knowledge/{id}")
    public Map<String, Object> deleteKnowledge(@PathVariable String id) {
        aiService.deleteKnowledge(id);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "删除成功");
        return result;
    }

    /**
     * 五、触发知识库索引
     */
    @PostMapping("/knowledge/index/{id}")
    public Map<String, Object> indexKnowledge(@PathVariable String id) {
        aiService.indexKnowledge(id);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "索引任务已提交");
        return result;
    }

    /**
     * 六、同步项目接口到知识库
     */
    @PostMapping("/knowledge/sync-api")
    public Map<String, Object> syncProjectApis(@RequestParam String projectId) {
        aiService.syncProjectApis(projectId);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "接口同步成功");
        return result;
    }

    // ==================== 会话管理 ====================

    /**
     * 七、获取会话列表
     */
    @GetMapping("/chat/history")
    public Map<String, Object> getConversationList(@RequestParam String projectId, @RequestParam String userId) {
        List<AiConversation> list = aiService.getConversationList(projectId, userId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        return result;
    }

    /**
     * 八、获取会话详情
     */
    @GetMapping("/chat/{id}")
    public Map<String, Object> getConversationDetail(@PathVariable String id) {
        AiConversation conversation = aiService.getConversationDetail(id);
        Map<String, Object> result = new HashMap<>();
        result.put("data", conversation);
        return result;
    }

    /**
     * 九、创建新会话
     */
    @PostMapping("/chat")
    public Map<String, Object> createConversation(@RequestBody Map<String, Object> request) {
        String projectId = (String) request.get("projectId");
        String userId = (String) request.get("userId");
        String sessionType = (String) request.getOrDefault("sessionType", "chat");
        Boolean useRag = (Boolean) request.getOrDefault("useRag", true);
        String conversationId = aiService.createConversation(projectId, userId, sessionType, useRag);
        Map<String, Object> result = new HashMap<>();
        result.put("data", conversationId);
        return result;
    }

    /**
     * 十、删除会话
     */
    @DeleteMapping("/chat/{id}")
    public Map<String, Object> deleteConversation(@PathVariable String id) {
        aiService.deleteConversation(id);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "删除成功");
        return result;
    }

    // ==================== AI对话 ====================

    /**
     * 十一、AI对话（SSE流式）
     */
    @PostMapping("/chat/stream")
    public SseEmitter chatStream(@RequestBody Map<String, Object> request) {
        SseEmitter emitter = new SseEmitter(300000L); // 5分钟超时
        
        CompletableFuture.runAsync(() -> {
            try {
                String projectId = (String) request.get("projectId");
                String message = (String) request.get("message");
                Boolean useRag = (Boolean) request.getOrDefault("useRag", true);
                String conversationId = (String) request.get("conversationId");
                
                // 创建或获取会话
                if (conversationId == null || conversationId.isEmpty()) {
                    conversationId = aiService.createConversation(projectId, 
                        (String) request.get("userId"), "chat", useRag);
                }
                
                // 保存用户消息
                aiService.saveConversationMessage(conversationId, "user", message);
                
                // 构建转发请求
                Map<String, Object> aiRequest = new HashMap<>();
                aiRequest.put("project_id", projectId);
                aiRequest.put("message", message);
                aiRequest.put("use_rag", useRag);
                aiRequest.put("conversation_id", conversationId);
                
                // 调用AI服务（简化处理，实际应该使用SSE）
                Map<String, Object> aiResponse = aiService.chat(aiRequest);
                
                // 发送响应
                String content = (String) aiResponse.get("content");
                if (content != null) {
                    emitter.send(SseEmitter.event()
                        .data("{\"type\": \"content\", \"delta\": \"" + content + "\"}"));
                }
                
                // 保存AI响应
                aiService.saveConversationMessage(conversationId, "assistant", content);
                
                emitter.send(SseEmitter.event()
                    .data("{\"type\": \"end\"}"));
                emitter.complete();
                
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });
        
        return emitter;
    }

    // ==================== 用例生成 ====================

    /**
     * 十二、生成测试用例
     */
    @PostMapping("/generate/case")
    public Map<String, Object> generateCase(@RequestBody Map<String, Object> request) {
        Map<String, Object> result = aiService.generateCase(request);
        return result;
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

    // ==================== 配置管理 ====================

    /**
     * 十四、获取AI配置
     */
    @GetMapping("/config")
    public Map<String, Object> getAiConfig(@RequestParam String projectId) {
        Map<String, String> config = aiService.getAiConfig(projectId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", config);
        return result;
    }

    /**
     * 十五、保存AI配置
     */
    @PostMapping("/config")
    public Map<String, Object> saveAiConfig(@RequestBody Map<String, Object> request) {
        String projectId = (String) request.get("projectId");
        String configKey = (String) request.get("configKey");
        String configValue = (String) request.get("configValue");
        aiService.saveAiConfig(projectId, configKey, configValue);
        Map<String, Object> result = new HashMap<>();
        result.put("msg", "配置保存成功");
        return result;
    }
}

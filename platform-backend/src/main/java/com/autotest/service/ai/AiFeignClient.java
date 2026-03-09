package com.autotest.service.ai;

import feign.Response;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * AI远程调用客户端
 * 职责：统一封装后端到 FastAPI 的 HTTP 转发，避免控制层直接拼接 URL。
 */
@FeignClient(name = "aiFeignClient", url = "${ai.service.base-url:http://127.0.0.1:8001}")
public interface AiFeignClient {

    /**
     * 转发流式聊天请求，返回原始 SSE 响应流。
     */
    @PostMapping("/ai/chat/stream")
    Response streamChat(@RequestBody Map<String, Object> request,
            @RequestHeader("token") String token);

    /**
     * 转发 Agent 用例生成请求。
     */
    @PostMapping("/ai/agent/generate-case")
    Map<String, Object> generateCase(@RequestBody Map<String, Object> request,
            @RequestHeader("token") String token);

    /**
     * 获取 Agent 可选接口列表。
     */
    @GetMapping("/ai/agent/api-list/{projectId}")
    Map<String, Object> getAgentApiList(@PathVariable("projectId") String projectId,
            @RequestHeader("token") String token);

    /**
     * 触发知识文档向量化写入。
     */
    @PostMapping("/ai/rag/add")
    Map<String, Object> addRag(@RequestBody Map<String, Object> request);

    /**
     * 删除知识文档对应向量分片。
     */
    @PostMapping("/ai/rag/delete")
    Map<String, Object> deleteRag(@RequestBody Map<String, Object> request);
}

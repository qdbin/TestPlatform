package com.autotest.controller;

import com.autotest.service.ai.AiPermissionService;
import com.autotest.service.ai.AiSchemaService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.Map;

/**
 * AI Schema 控制器
 * 职责：暴露场景化 schema 抽取接口，避免控制层耦合 OpenAPI 解析细节。
 */
@RestController
@RequestMapping("/autotest/ai/schema")
public class AiSchemaController {

    @Resource
    private AiPermissionService aiPermissionService;

    @Resource
    private AiSchemaService aiSchemaService;

    @GetMapping("/{scene}")
    public Map<String, Object> getSchemaByScene(@PathVariable String scene,
            @RequestParam String projectId,
            HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        return aiSchemaService.getSceneSchema(scene, request);
    }

    @GetMapping("/extract")
    public Map<String, Object> getSchemaByNames(@RequestParam String projectId,
            @RequestParam String names,
            HttpServletRequest request) {
        aiPermissionService.assertProjectAccess(request, projectId);
        return aiSchemaService.extractSchemaByNames(names, request);
    }

    @GetMapping("/case")
    public Map<String, Object> getCaseSchema(@RequestParam String projectId, HttpServletRequest request) {
        return getSchemaByScene("case", projectId, request);
    }
}

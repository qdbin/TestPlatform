package com.autotest.service.ai;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.*;

/**
 * Schema 抽取服务
 * 职责：基于 OpenAPI 文档按场景抽取请求 Schema，供 AI 生成约束使用。
 */
@Service
public class AiSchemaService {

    @Resource
    private RestTemplate restTemplate;

    private static final Map<String, String> SCHEMA_GROUPS = new HashMap<>();

    static {
        SCHEMA_GROUPS.put("case", "CaseRequest,CaseApiRequest"); // 用例生成场景
    }

    /**
     * 根据场景名读取预置 schema 组合。
     */
    public Map<String, Object> getSceneSchema(String scene, HttpServletRequest request) {
        String names = SCHEMA_GROUPS.getOrDefault(String.valueOf(scene).toLowerCase(Locale.ROOT), "");
        return extractSchemaByNames(names, request);
    }

    /**
     * 按名称列表抽取 schema，names 以逗号分隔。
     */
    public Map<String, Object> extractSchemaByNames(String names, HttpServletRequest request) {
        String contextUrl = request.getScheme() + "://" + request.getServerName() + ":" + request.getServerPort();
        Map<String, Object> openapi = restTemplate.getForObject(contextUrl + "/v3/api-docs", Map.class);
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
        return data;
    }
}

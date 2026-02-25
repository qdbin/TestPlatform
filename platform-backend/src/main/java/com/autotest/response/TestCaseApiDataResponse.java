package com.autotest.response;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

/**
 * 响应：API用例接口数据
 * 用途：承载单个接口的请求数据与断言结果
 */
@Setter
@Getter
public class TestCaseApiDataResponse {

    @JSONField(ordinal = 1)
    private String apiId;         // 接口ID

    @JSONField(ordinal = 2)
    private String apiName;       // 接口名称

    @JSONField(ordinal = 3)
    private String apiDesc;       // 接口描述

    @JSONField(ordinal = 4)
    private String url;           // 完整URL（含域名）

    @JSONField(ordinal = 5)
    private String path;          // 路径（不含域名）

    @JSONField(ordinal = 6)
    private String method;        // 请求方法（GET/POST等）

    @JSONField(ordinal = 7)
    private String protocol;      // 协议（HTTP/HTTPS）

    @JSONField(ordinal = 8)
    private JSONObject headers;   // 请求头

    @JSONField(ordinal = 9)
    private JSONObject proxies;   // 代理设置

    @JSONField(ordinal = 10)
    private JSONObject body;      // 请求体数据

    @JSONField(ordinal = 11)
    private JSONObject query;     // Query参数

    @JSONField(ordinal = 12)
    private JSONObject rest;      // REST路径参数

    @JSONField(ordinal = 13)
    private JSONArray assertions; // 断言列表

    @JSONField(ordinal = 14)
    private JSONArray relations;  // 关联关系（依赖/前后置）

    @JSONField(ordinal = 15)
    private JSONObject controller; // 控制器扩展配置

}

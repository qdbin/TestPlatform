package com.autotest.request;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import lombok.Getter;
import lombok.Setter;


/**
 * 实体：API用例步骤请求
 * 用途：承载用例中单个接口步骤的入参与校验
 */
@Setter
@Getter
public class CaseApiRequest {
    private String id;            // 步骤ID

    private Long index;           // 步骤序号（从0或1开始）

    private String caseId;        // 归属用例ID

    private String apiId;         // 关联接口ID

    private String description;   // 步骤描述

    private JSONArray header;     // 请求头参数

    private JSONObject body;      // 请求体参数

    private JSONArray query;      // 查询参数

    private JSONArray rest;       // REST路径参数

    private JSONArray assertion;  // 断言集合

    private JSONArray relation;   // 变量提取与传递关系

    private JSONArray controller; // 控制器（前后置动作）

}

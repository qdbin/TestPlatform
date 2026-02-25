package com.autotest.request;

import com.alibaba.fastjson.JSONArray;
import lombok.Getter;
import lombok.Setter;

/**
 * 请求：Web用例步骤
 * 用途：承载Web自动化用例每个步骤的入参
 */

@Setter
@Getter
public class CaseWebRequest {
    private String id;           // 步骤ID

    private Long index;          // 步骤序号

    private String caseId;       // 归属用例ID

    private String operationId;  // 关联操作ID

    private String description;  // 步骤描述

    private JSONArray element;   // 元素定位列表

    private JSONArray data;      // 操作数据列表

}

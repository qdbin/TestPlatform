package com.autotest.response;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：测试用例响应载体
 * 用途：封装用例执行所需函数与参数
 */
@Setter
@Getter
public class TestCaseResponse {

    @JSONField(ordinal = 1)
    private String comment; // 注释/说明

    @JSONField(ordinal = 2)
    private String caseId; // 用例ID

    @JSONField(ordinal = 3)
    private String caseName; // 用例名称

    @JSONField(ordinal = 4)
    private JSONArray functions; // 执行函数集合

    @JSONField(ordinal = 5)
    private JSONObject params; // 全局参数

}

package com.autotest.response;

import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

/**
 * 响应：Web用例步骤明细
 * 用途：承载Web自动化用例每一步的操作信息与数据
 */
@Setter
@Getter
public class TestCaseWebDataResponse {

    @JSONField(ordinal = 1)
    private String operationType;    // 操作类型（click/input等）

    @JSONField(ordinal = 2)
    private String operationId;      // 操作ID（控件/脚本标识）

    @JSONField(ordinal = 3)
    private String operationName;    // 操作名称

    @JSONField(ordinal = 4)
    private String operationDesc;    // 操作描述

    @JSONField(ordinal = 5)
    private String operationTrans;   // 事务名称/标识

    @JSONField(ordinal = 6)
    private String operationCode;    // 操作编码（步骤序号）

    @JSONField(ordinal = 7)
    private JSONObject operationElement; // 操作元素（定位信息）

    @JSONField(ordinal = 8)
    private JSONObject operationData;    // 操作数据（输入/选择值）

}

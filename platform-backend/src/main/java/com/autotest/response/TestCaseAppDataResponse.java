package com.autotest.response;

import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

/**
 * 响应：APP用例单步数据结构
 * 用途：描述每个APP操作的类型、系统、元素与数据
 */
@Setter
@Getter
public class TestCaseAppDataResponse {

    @JSONField(ordinal = 1)
    private String operationType;    // 操作类型（click/input等）

    @JSONField(ordinal = 2)
    private String operationSystem;  // 操作归属系统（android/ios）

    @JSONField(ordinal = 3)
    private String operationId;      // 操作ID（控件/脚本标识）

    @JSONField(ordinal = 4)
    private String operationName;    // 操作名称

    @JSONField(ordinal = 5)
    private String operationDesc;    // 操作描述

    @JSONField(ordinal = 6)
    private String operationTrans;   // 事务名称/标识

    @JSONField(ordinal = 7)
    private String operationCode;    // 操作编码（用例内序号）

    @JSONField(ordinal = 8)
    private JSONObject operationElement; // 操作元素（定位信息）

    @JSONField(ordinal = 9)
    private JSONObject operationData;    // 操作数据（输入/选择值）

}

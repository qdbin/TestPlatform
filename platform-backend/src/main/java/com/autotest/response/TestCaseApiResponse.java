package com.autotest.response;

import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 响应：API用例运行结果聚合
 * 用途：承载用例的接口列表及基础信息
 */
@Setter
@Getter
public class TestCaseApiResponse extends TestCaseResponse{

    @JSONField(ordinal = 6)
    private List<TestCaseApiDataResponse> apiList; // API用例的接口列表

}

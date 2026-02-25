package com.autotest.response;

import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.annotation.JSONField;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 响应：Web 用例执行配置与步骤
 * 用途：承载 Web 场景的驱动配置与操作步骤列表，
 *      结合父类 `TestCaseResponse` 的通用用例信息用于下发与展示。
 */
@Setter
@Getter
public class TestCaseWebResponse extends TestCaseResponse{

    @JSONField(ordinal = 6)
    private Boolean startDriver;   // 是否在用例开始时启动浏览器驱动

    @JSONField(ordinal = 7)
    private Boolean closeDriver;   // 是否在用例结束时关闭浏览器驱动

    @JSONField(ordinal = 8)
    private JSONObject driverSetting; // 浏览器驱动的配置参数（如超时、分辨率等）

    @JSONField(ordinal = 9)
    private List<TestCaseWebDataResponse> optList; // WEB用例的操作列表

}

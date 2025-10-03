package com.autotest.response;

import com.autotest.common.constants.ResponseCode;
import lombok.Data;

/**
 * 响应：统一模板载体
 * 用途：按平台规范封装控制层返回（status:message:data）
 */
@Data
public class TemplateResponse<T> {

    private int status;      // 状态码（参考 ResponseCode）

    private String message;  // 状态说明信息

    private T data;          // 业务数据载体（泛型）

    /**
     * 成功响应构造（默认 SUCCESS）
     *
     * @param data // 成功返回的数据
     */
    public TemplateResponse(T data) {
        this(ResponseCode.SUCCESS, data);
    }

    /**
     * 自定义响应构造（含状态码）
     *
     * @param resultCode // 平台响应码
     * @param data       // 返回数据
     *
     * 示例：
     *   入参：resultCode=ResponseCode.FAILED, data="原因"
     *   调用：new TemplateResponse<>(resultCode, data)
     *   返回：{"status":500,"message":"失败","data":"原因"}
     */
    public TemplateResponse(ResponseCode resultCode, T data) {
        this.status = resultCode.getStatus();
        this.message = resultCode.getMessage();
        this.data = data;
    }
}
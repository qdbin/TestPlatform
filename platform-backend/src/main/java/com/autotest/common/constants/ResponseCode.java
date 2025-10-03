package com.autotest.common.constants;

import lombok.Getter;

/**
 * 常量：通用响应码（status:message）
 * 用途：统一接口返回状态及文案
 */
@Getter
public enum ResponseCode {
    SUCCESS(0, "成功"), // 请求成功

    FAILED(1000, "失败"), // 常规失败

    VALIDATE_FAILED(1002, "参数校验失败"), // 参数校验失败

    DUPLICATE_FAILED(1003, "重复校验失败"), // 重复性校验失败

    LOGIN_FAILED(2010, "登录失败"), // 登录失败

    PASSWORD_FAILED(2015, "密码错误"), // 密码错误

    TOKEN_EMPTY(2020, "登录信息获取失败 请重新登录"), // token为空

    TOKEN_EXPIRE(2030, "登录已过期 请重新登录"), // token过期

    TOKEN_FAILED(2040, "登录信息校验失败 请重新登录"), // token校验失败

    ENGINE_FAILED(2050, "引擎code及secret验证失败"), // 引擎鉴权失败

    UPLOAD_FAILED(3010, "文件上传失败"), // 上传失败

    ERROR(5000, "未知错误"); // 未知错误

    private final int status; // 状态码
    private final String message; // 文案消息

    ResponseCode(int status, String message) {
        this.status = status;
        this.message = message;
    }
}

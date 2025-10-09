package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

/**
 * 实体：登录请求载体（account:password）
 * 用途：承载登录接口的账号与密码
 */
@Setter
@Getter
public class LoginRequest {
    private String account;  // 登录账号
    private String password; // 登录密码
}

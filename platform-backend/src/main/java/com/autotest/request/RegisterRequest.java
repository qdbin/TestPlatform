package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

/**
 * 请求：用户注册信息
 * 用途：承载注册所需的账号、联系方式与凭据
 */
@Setter
@Getter
public class RegisterRequest {

    private String account;

    private Long mobile;

    private String username;

    private String email;

    private String password;

}

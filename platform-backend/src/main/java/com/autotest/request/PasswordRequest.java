package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

/**
 * 请求：用户修改密码
 * 用途：校验旧密码并设置新密码所需参数
 */
@Setter
@Getter
public class PasswordRequest {
    private String userId;
    private String oldPassword;
    private String newPassword;
}

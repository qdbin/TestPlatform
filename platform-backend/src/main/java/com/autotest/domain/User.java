package com.autotest.domain;

import java.io.Serializable;
import lombok.Data;

/**
 * 实体：用户（username:account）
 * 用途：平台用户账户与基础信息
 */
@Data
public class User implements Serializable {
    private String id; // 主键ID

    private String username; // 用户名

    private String account; // 账户名

    private String password; // 密码

    private String status; // 状态

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private Long mobile; // 手机号

    private String lastProject; // 最近项目ID

    private String email; // 邮箱
}
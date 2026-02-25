package com.autotest.dto;

import lombok.Data;

/**
 * DTO：数据库连接信息
 * 用途：承载数据库连接的基础配置（主机、端口、账号、密码）
 */
@Data
public class DBConnectInfo {
    private String host;     // 数据库主机地址

    private String port;     // 数据库端口

    private String user;     // 连接用户名

    private String password; // 连接密码
}

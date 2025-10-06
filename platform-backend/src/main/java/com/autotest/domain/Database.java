package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：数据库连接配置
 * 用途：存储环境下数据库类型与连接信息
 */
@Data
public class Database implements Serializable {
    private String id;               // 主键ID

    private String databaseType;     // 数据库类型（MySQL/Oracle等）

    private String databaseKey;      // 数据库标识键（环境内唯一）

    private String connectInfo;      // 连接信息JSON字符串

    private String environmentId;    // 环境ID

    private Long createTime;         // 创建时间戳

    private Long updateTime;         // 更新时间戳

    private String createUser;       // 创建人ID

    private String updateUser;       // 更新人ID

    private Integer status;          // 状态（1正常/0删除）
}
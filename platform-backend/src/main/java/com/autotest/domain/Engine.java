package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：执行引擎（name:type）
 * 用途：引擎注册与心跳信息
 */
@Data
public class Engine implements Serializable {
    private String id; // 主键ID

    private String name; // 引擎名称

    private String engineType; // 引擎类型

    private String secret; // 引擎密钥

    private String status; // 状态

    private Long lastHeartbeatTime; // 最近心跳时间

    private String projectId; // 所属项目ID

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

}
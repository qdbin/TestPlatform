package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：用例集合（Collection）
    * 用途：管理一组用例或任务的版本化集合
    */
@Data
public class Collection implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 集合名称

    private String deviceId;      // 设备ID（执行设备）

    private String versionId;     // 集合版本ID

    private String description;   // 集合描述

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String createUser;    // 创建人

    private String updateUser;    // 更新人

    private Integer status;       // 状态（启用/禁用）

}
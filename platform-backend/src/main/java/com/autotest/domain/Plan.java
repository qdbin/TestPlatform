package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：测试计划（name:version:env）
 * 用途：定义计划的版本、环境、并发与重试策略等
 */
@Data
public class Plan implements Serializable {
    private String id;             // 主键ID

    private String name;           // 计划名称

    private String versionId;      // 关联版本ID

    private String description;    // 描述

    private String environmentId;  // 执行环境ID

    private Integer maxThread;     // 最大并发线程数

    private String retry;          // 重试策略（如次数/间隔）

    private String engineId;       // 指定执行引擎ID

    private String projectId;      // 所属项目ID

    private Long createTime;       // 创建时间戳

    private Long updateTime;       // 更新时间戳

    private String createUser;     // 创建人

    private String updateUser;     // 更新人

    private Integer status;        // 状态（1正常/0删除）

}
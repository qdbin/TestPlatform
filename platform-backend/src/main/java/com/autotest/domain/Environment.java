package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：环境（name:projectId）
 * 用途：项目环境配置与说明
 */
@Data
public class Environment implements Serializable {
    private String id; // 主键ID

    private String name; // 环境名称

    private String projectId; // 所属项目ID

    private String description; // 描述说明

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private Integer status; // 状态（启用/禁用）

}
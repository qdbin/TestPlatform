package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：模块信息（name:projectId）
 * 用途：承载项目内模块的层级结构与归属
 */
@Data
public class Module implements Serializable {
    private String id;          // 主键ID

    private String name;        // 模块名称

    private String parentId;    // 父模块ID（根为"0"）

    private String projectId;   // 所属项目ID

    private Long createTime;    // 创建时间戳

    private Long updateTime;    // 更新时间戳

    private String createUser;  // 创建人ID

    private String updateUser;  // 更新人ID
}
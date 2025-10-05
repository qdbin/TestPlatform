package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：参数分组（ParamGroup）
    * 用途：管理测试参数的分组与类型
    */
@Data
public class ParamGroup implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 分组名称

    private String paramType;     // 参数类型（如全局、环境等）

    private String projectId;     // 所属项目ID

    private String description;   // 分组描述

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String createUser;    // 创建人

    private String updateUser;    // 更新人

}
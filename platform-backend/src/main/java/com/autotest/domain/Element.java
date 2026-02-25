package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：页面元素定义
 * 用途：存储定位方式与表达式等信息
 */
@Data
public class Element implements Serializable {
    private String id;            // 主键ID

    private Long num;             // 序号（排序）

    private String name;          // 元素名称

    private String moduleId;      // 所属模块ID

    private String projectId;     // 所属项目ID

    private String by;            // 定位方式（id/xpath/css等）

    private String expression;    // 定位表达式

    private String description;   // 描述信息

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String createUser;    // 创建人ID

    private String updateUser;    // 更新人ID

    private String status;        // 状态（Normal/删除）

}
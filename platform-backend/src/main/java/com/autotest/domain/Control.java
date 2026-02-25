package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：控件元素（system:by/expression）
 * 用途：存储桌面/移动端控件的定位方式与表达式
 */
@Data
public class Control implements Serializable {
    private String id;            // 主键ID

    private Long num;             // 序号（排序）

    private String name;          // 控件名称

    private String system;        // 终端系统（WEB/APP/PC等）

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
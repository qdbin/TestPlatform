package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：项目（name:admin）
 * 用途：项目信息与负责人
 */
@Data
public class Project implements Serializable {
    private String id; // 主键ID

    private String name; // 项目名称

    private String description; // 描述说明

    private String projectAdmin; // 项目管理员ID

    private String status; // 状态

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳
}
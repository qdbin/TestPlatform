package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：测试用例（name:type）
 * 用途：承载用例基础信息与类型标识
 */
@Data
public class Case implements Serializable {
    private String id; // 主键ID

    private Long num; // 序号/编号

    private String name; // 用例名称

    private String level; // 优先级/级别

    private String moduleId; // 模块ID

    private String projectId; // 项目ID

    private String type; // 用例类型（API/WEB/APP）

    private String thirdParty; // 第三方标识/外部系统

    private String description; // 描述说明

    private String environmentIds; // 关联环境IDs（逗号分隔）

    private String system; // 系统类型（web/app/android/apple等）

    private String commonParam; // 公共参数（JSON字符串）

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private String status; // 状态

}
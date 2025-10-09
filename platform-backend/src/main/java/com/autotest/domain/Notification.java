package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：通知配置（Notification）
    * 用途：项目内通知渠道配置与参数存储
    */
@Data
public class Notification implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 通知名称

    private String type;          // 通知类型（如邮件、Webhook等）

    private String params;        // 通知参数JSON字符串

    private String webhookUrl;    // Webhook地址

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String status;        // 状态（启用/禁用）

}

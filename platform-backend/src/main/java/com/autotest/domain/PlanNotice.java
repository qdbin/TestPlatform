package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：计划通知配置
 * 用途：绑定计划与通知渠道，并设置触发条件
 */
@Data
public class PlanNotice implements Serializable {
    private String id;               // 主键ID

    private String planId;           // 关联计划ID

    private String notificationId;   // 通知渠道ID

    private String condition;        // 触发条件（如失败/全部）

}
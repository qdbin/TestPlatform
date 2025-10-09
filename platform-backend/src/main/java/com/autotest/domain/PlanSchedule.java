package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：计划调度配置
 * 用途：记录计划开始时间、执行频率与下次运行时间
 */
@Data
public class PlanSchedule implements Serializable {
    private String id;           // 主键ID

    private String planId;       // 关联计划ID

    private String startTime;    // 开始时间（ISO字符串）

    private String frequency;    // 执行频率（HALF_HOUR/ONE_HOUR/ONE_DAY/ONE_WEEK/ONE_MONTH/ONLY_ONE）

    private Long nextRunTime;    // 下次运行时间戳（ms）

}
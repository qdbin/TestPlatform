package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：测试报告（name:taskId）
 * 用途：记录任务执行的起止时间与状态、来源及环境设备信息
 */
@Data
public class Report implements Serializable {
    private String id; // 主键ID

    private String name; // 报告名称

    private String taskId; // 关联任务ID

    private String environmentId; // 执行环境ID

    private String deviceId; // 设备ID

    private String sourceType; // 来源类型（PLAN/DEBUG等）

    private String sourceId; // 来源ID（计划/调试ID）

    private Long startTime; // 开始时间戳

    private Long endTime; // 结束时间戳

    private String status; // 报告状态（SUCCESS/FAIL/ERROR）

    private String projectId; // 项目ID

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

}
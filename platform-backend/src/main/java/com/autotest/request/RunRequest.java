package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

/**
 * 实体：执行任务请求（engine:source）
 * 用途：承载任务发起的引擎、环境、来源等信息
 */
@Setter
@Getter
public class RunRequest {
    private String engineId;       // 引擎实例ID
    private String environmentId;  // 环境ID
    private String deviceId;       // 设备ID（可选）
    private String sourceType;     // 来源类型（temp/case/collection/plan）
    private String sourceId;       // 来源主键ID
    private String sourceName;     // 来源名称
    private String taskType;       // 任务类型（DeBug/SCHEDULE/MANUAL）
    private String runUser;        // 执行人（由服务端填充）
    private String projectId;      // 项目ID

    private CaseRequest debugData; // 调试数据（CaseRequest）

    private String user;           // 请求用户（兼容旧字段）
    private String planId;         // 计划ID（当来源类型为计划）
}

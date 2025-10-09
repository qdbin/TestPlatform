package com.autotest.dto;

import com.autotest.domain.Task;
import lombok.Getter;
import lombok.Setter;

/**
    * 获取Task相关的源信息（用户名、报告ID、来源、环境、设备）（依据 task.id=report.id）
    */
@Getter
@Setter
public class TaskDTO extends Task {

    private String username;        // 任务关联的用户名（展示）

    private String reportId;        // 任务对应的报告ID

    private String sourceType;      // 来源类型（plan/case等）

    private String sourceId;        // 来源ID（计划/用例ID）

    private String environmentId;   // 环境ID

    private String deviceId;        // 设备ID

}

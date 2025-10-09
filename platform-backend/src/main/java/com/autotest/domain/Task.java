package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：任务（Task）
    * 用途：测试任务或计划的执行信息记录
    */
@Data
public class Task implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 任务名称

    private String type;          // 任务类型（如计划/即时）

    private String status;        // 任务状态

    private String engineId;      // 执行引擎ID

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String createUser;    // 创建人

    private String updateUser;    // 更新人

}
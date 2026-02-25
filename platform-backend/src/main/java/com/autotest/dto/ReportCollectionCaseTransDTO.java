package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;


/**
 * 实体：报告集合用例事务明细
 * 用途：承载单个事务执行的状态、日志、耗时与附件
 */
@Getter
@Setter
public class ReportCollectionCaseTransDTO {

    private String status;          // 事务状态（pass/fail/error等）

    private String transId;         // 事务ID

    private String transName;       // 事务名称

    private String content;         // 事务内容（执行脚本/步骤概述）

    private String description;     // 事务描述

    private String execLog;         // 执行日志（文本）

    private String during;          // 耗时（ms）

    private String screenshotList;  // 截图列表（JSON字符串或ID串）

    private Boolean showViewer = false; // 是否在前端展示查看器

}

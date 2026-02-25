package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: ReportCollectionCaseApp
 * 职责: 集合用例中APP步骤的执行记录明细
 */
@Data
public class ReportCollectionCaseApp implements Serializable {
    private String id;                       // 主键ID

    private String reportCollectionCaseId;   // 所属集合用例报告ID

    private Integer caseAppIndex;            // APP步骤顺序

    private String operationId;              // 操作ID

    private String operationName;            // 操作名称

    private String operationElement;         // 操作元素

    private String description;              // 步骤描述

    private String screenshot;               // 截图路径

    private String execLog;                  // 执行日志

    private String status;                   // 执行状态

}
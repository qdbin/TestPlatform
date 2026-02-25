package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: ReportCollectionCaseApi
 * 职责: 集合用例中API步骤的执行记录明细
 */
@Data
public class ReportCollectionCaseApi implements Serializable {
    private String id;                       // 主键ID

    private String reportCollectionCaseId;   // 所属集合用例报告ID

    private Integer caseApiIndex;            // API步骤顺序

    private String apiId;                    // 接口ID

    private String apiName;                  // 接口名称

    private String apiPath;                  // 接口路径

    private String description;              // 步骤描述

    private String execLog;                  // 执行日志

    private Integer during;                  // 执行耗时(ms)

    private String status;                   // 执行状态

}
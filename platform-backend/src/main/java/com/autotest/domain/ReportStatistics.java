package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：报告统计信息
 * 用途：记录报告的用例总数与通过/失败/错误计数
 */
@Data
public class ReportStatistics implements Serializable {
    private String id;          // 主键ID

    private String reportId;    // 报告ID

    private Integer total;      // 用例总数

    private Integer passCount;  // 通过数量

    private Integer failCount;  // 失败数量

    private Integer errorCount; // 错误数量

}
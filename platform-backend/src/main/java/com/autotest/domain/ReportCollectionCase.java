package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: ReportCollectionCase
 * 职责: 测试报告中集合用例执行记录的概要信息
 */
@Data
public class ReportCollectionCase implements Serializable {
    private String id;                    // 主键ID

    private String reportCollectionId;    // 所属报告集合ID

    private Integer collectionCaseIndex;  // 集合用例执行顺序

    private String caseId;                // 用例ID

    private String caseType;              // 用例类型(API/WEB/APP)

    private String caseName;              // 用例名称

    private String caseDesc;              // 用例描述

    private Integer runTimes;             // 执行次数

    private Long startTime;               // 开始时间戳

    private Long endTime;                 // 结束时间戳

    private String during;                // 执行时长描述

    private String status;                // 执行状态

}
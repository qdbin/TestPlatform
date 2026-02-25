package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：报告集合关联（ReportCollection）
    * 用途：测试报告与集合版本的关联信息
    */
@Data
public class ReportCollection implements Serializable {
    private String id;                // 唯一标识ID

    private String reportId;          // 报告ID

    private String collectionId;      // 集合ID

    private String collectionName;    // 集合名称

    private String collectionVersion; // 集合版本号

    private Integer caseTotal;        // 用例总数

}
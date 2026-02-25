package com.autotest.dto;

import com.autotest.domain.ReportCollection;
import lombok.Getter;
import lombok.Setter;

import java.util.List;


/**
 * 实体：报告-集合扩展DTO（继承 ReportCollection）
 * 用途：承载集合维度的统计与用例明细列表
 */
@Getter
@Setter
public class ReportCollectionDTO extends ReportCollection {
    private Integer passCount;   // 通过用例数量

    private Integer failCount;   // 失败用例数量

    private Integer errorCount;  // 错误用例数量

    private List<ReportCollectionCaseDTO> caseList; // 集合下的用例执行明细列表

}

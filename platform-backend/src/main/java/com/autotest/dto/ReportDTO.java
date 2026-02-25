package com.autotest.dto;

import com.autotest.domain.Report;
import lombok.Getter;
import lombok.Setter;

import java.util.List;


/**
 * 实体：报告扩展DTO（继承 Report）
 * 用途：承载报告展示附加字段与集合明细
 */
@Getter
@Setter
public class ReportDTO extends Report {

    private String username;    // 执行人名字（展示）

    private Long total;

    private Long passCount;

    private Long failCount;

    private Long errorCount;

    private String passRate;

    private Integer progress;

    private List<ReportCollectionDTO> collectionList; // 报告下的集合列表（含各集合用例与统计）

}

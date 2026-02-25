package com.autotest.dto;

import com.autotest.domain.ReportCollectionCase;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：报告-集合用例扩展DTO
 * 
 *     用途：承载单个集合用例的执行过程明细（事务transList）等展示字段，便于前端渲染步骤详情与附件信息。
 */
@Getter
@Setter
public class ReportCollectionCaseDTO extends ReportCollectionCase {

    private List<ReportCollectionCaseTransDTO> transList; // 执行事务明细列表（每项包含状态、日志、截图等）

}

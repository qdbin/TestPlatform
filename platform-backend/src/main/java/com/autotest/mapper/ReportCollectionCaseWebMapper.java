package com.autotest.mapper;

import com.autotest.domain.ReportCollectionCaseWeb;
import com.autotest.dto.ReportCollectionCaseTransDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * MyBatis Mapper：报告集合-Web用例步骤与结果
 * 负责 Web 用例执行记录的批量写入、查询以及清理操作
 */
@Mapper
public interface ReportCollectionCaseWebMapper {
    /**
     * 批量写入 Web 用例执行记录
     * @param reportCollectionCaseWebs 记录列表
     */
    void batchAddReportCollectionCaseWeb(List<ReportCollectionCaseWeb> reportCollectionCaseWebs);

    /**
     * 查询指定用例的 Web 步骤执行明细
     * @param reportCaseId 报告用例ID
     * @return 步骤明细列表
     */
    List<ReportCollectionCaseTransDTO> getReportCaseActionList(String reportCaseId);

    /**
     * 删除指定报告的所有 Web 用例执行记录
     * @param reportId 报告ID
     */
    void deleteByReportId(String reportId);
}
package com.autotest.mapper;

import com.autotest.domain.ReportCollectionCaseApi;
import com.autotest.dto.ReportCollectionCaseTransDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * MyBatis Mapper：报告集合-API用例步骤与结果
 * 负责 API 用例执行记录的批量写入、查询以及清理操作
 */
@Mapper
public interface ReportCollectionCaseApiMapper {
    /**
     * 批量写入 API 用例执行记录
     * @param reportCollectionCaseApis 记录列表
     */
    void batchAddReportCollectionCaseApi(List<ReportCollectionCaseApi> reportCollectionCaseApis);

    /**
     * 查询指定用例的 API 步骤执行明细
     * @param reportCaseId 报告用例ID
     * @return 步骤明细列表
     */
    List<ReportCollectionCaseTransDTO> getReportCaseActionList(String reportCaseId);

    /**
     * 查询某接口的最近一次报告ID
     * @param apiId 接口ID
     * @return 报告ID
     */
    String getLastApiReport(String apiId);

    /**
     * 删除指定报告的所有 API 用例执行记录
     * @param reportId 报告ID
     */
    void deleteByReportId(String reportId);
}
package com.autotest.mapper;

import com.autotest.domain.ReportCollectionCase;
import com.autotest.dto.ReportCollectionCaseDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * MyBatis Mapper：报告-集合-用例结果
 * 负责报告集合下用例执行结果的写入、统计、查询与清理
 */
@Mapper
public interface ReportCollectionCaseMapper {
    /**
     * 新增一条集合用例执行结果
     * @param reportCollectionCase 集合用例结果实体
     */
    void addReportCollectionCase(ReportCollectionCase reportCollectionCase);

    /**
     * 统计报告维度的用例结果数量
     * @param status 结果状态：pass/fail/error
     * @param reportId 报告ID
     * @return 数量
     */
    Integer countReportResult(String status, String reportId);

    /**
     * 统计报告集合维度的用例结果数量
     * @param status 结果状态：pass/fail/error
     * @param reportCollectionId 报告集合ID
     * @return 数量
     */
    Integer countReportCollectionResult(String status, String reportCollectionId);

    /**
     * 根据任务ID查询对应的用例执行结果
     * @param taskId 任务ID
     * @return 用例执行结果DTO
     */
    ReportCollectionCaseDTO getCaseReportByTaskId(String taskId);

    /**
     * 查询报告集合下的用例结果列表
     * @param reportCollectionId 报告集合ID
     * @return 用例结果列表
     */
    List<ReportCollectionCaseDTO> getReportCollectionCaseList(String reportCollectionId);

    /**
     * 删除指定报告下的所有集合用例结果
     * @param reportId 报告ID
     */
    void deleteByReportId(String reportId);
}
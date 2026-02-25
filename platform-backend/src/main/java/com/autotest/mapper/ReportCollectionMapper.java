package com.autotest.mapper;

import com.autotest.domain.ReportCollection;
import com.autotest.dto.ReportCollectionDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;


/**
 * 映射：报告集合数据访问
 * 用途：查询报告集合详情与列表，新增及按报告ID清理集合
 */
@Mapper
public interface ReportCollectionMapper {
    /**
     * 查询报告集合详情
     *
     *     @param reportId     // 报告ID
     *     @param collectionId // 集合ID
     *     @return ReportCollection // 报告集合实体
     */
    ReportCollection getReportCollection(String reportId, String collectionId);

    /**
     * 查询报告下的集合列表
     *
     *     @param reportId // 报告ID
     *     @return List<ReportCollectionDTO> // 集合DTO列表
     */
    List<ReportCollectionDTO> getReportCollectionList(String reportId);

    /**
     * 新增报告集合
     *
     *     @param reportCollection // 报告集合实体
     *     @return void            // 无返回
     */
    void addReportCollection(ReportCollection reportCollection);

    /**
     * 按报告ID删除全部集合
     *
     *     @param reportId // 报告ID
     *     @return void    // 无返回
     */
    void deleteByReportId(String reportId);
}
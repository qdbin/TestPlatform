package com.autotest.mapper;

import com.autotest.domain.Report;
import com.autotest.domain.ReportStatistics;
import com.autotest.dto.ReportDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：报告数据访问层
 * 用途：提供报告新增/更新/删除、状态维护、分页与详情查询
 */
@Mapper
public interface ReportMapper {
    /**
     * 新增报告
     *
     *     @param report // 报告实体
     *     @return void  // 无返回
     */
    void addReport(Report report);

    /**
     * 新增报告统计
     *
     *     @param reportStatistics // 报告统计实体
     *     @return void            // 无返回
     */
    void addReportStatistics(ReportStatistics reportStatistics);

    /**
     * 获取报告统计
     *
     *     @param reportId            // 报告ID
     *     @return ReportStatistics   // 统计信息
     */
    ReportStatistics getReportStatistics(String reportId);

    /**
     * 查询超时报告
     *
     *     @param minLastUploadTime // 最小上传时间阈值
     *     @param minLastToRunTime  // 最小运行时间阈值
     *     @return List<Report>     // 超时报告列表
     */
    List<Report> selectTimeoutReport(Long minLastUploadTime, Long minLastToRunTime);

    /**
     * 更新报告开始时间
     *
     *     @param reportId  // 报告ID
     *     @param startTime // 开始时间戳
     *     @param updateTime // 更新时间戳
     *     @return void     // 无返回
     */
    void updateReportStartTime(String reportId, Long startTime, Long updateTime);

    /**
     * 更新报告结束时间
     *
     *     @param reportId  // 报告ID
     *     @param endTime   // 结束时间戳
     *     @param updateTime // 更新时间戳
     *     @return void     // 无返回
     */
    void updateReportEndTime(String reportId, Long endTime, Long updateTime);

    /**
     * 更新报告统计信息
     *
     *     @param reportStatistics // 报告统计实体
     *     @return void            // 无返回
     */
    void updateReportStatistics(ReportStatistics reportStatistics);

    /**
     * 删除报告
     *
     *     @param id   // 报告ID
     *     @return void // 无返回
     */
    void deleteReport(String id);

    /**
     * 更新报告状态（按ID）
     *
     *     @param status // 状态值（SUCCESS/FAIL/ERROR等）
     *     @param id     // 报告ID
     *     @return void  // 无返回
     */
    void updateReportStatus(String status, String id);

    /**
     * 更新报告状态（按任务ID）
     *
     *     @param status // 状态值
     *     @param taskId // 任务ID
     *     @return void  // 无返回
     */
    void updateReportStatusByTask(String status, String taskId);

    /**
     * 更新全部报告状态（按引擎ID）
     *
     *     @param status   // 状态值
     *     @param engineId // 引擎ID
     *     @return void    // 无返回
     */
    void updateAllReportStatusByEngine(String status, String engineId);

    /**
     * 分页查询报告列表
     *
     *     @param request           // 查询请求（项目/条件/状态/时间范围）
     *     @return List<ReportDTO>  // 报告列表
     */
    List<ReportDTO> getReportList(QueryRequest request);

    /**
     * 获取报告详情
     *
     *     @param reportId  // 报告ID
     *     @return ReportDTO // 报告详情（含集合、用例统计）
     */
    ReportDTO getReportDetail(String reportId);

}
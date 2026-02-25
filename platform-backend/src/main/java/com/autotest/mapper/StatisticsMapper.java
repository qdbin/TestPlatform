package com.autotest.mapper;

import com.autotest.domain.DailyStatistics;
import com.autotest.domain.SumStatistics;
import com.autotest.dto.StatisticsDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：项目统计数据访问（daily:sum）
 * 用途：维护日维度与汇总维度统计，并提供各类排行榜/计数查询
 */
@Mapper
public interface StatisticsMapper {
    /**
     * 批量更新日统计数据
     *
     * @param dailyStatisticsList // 每日统计列表
     * @return void               // 无返回
     */
    void updateDailyData(List<DailyStatistics> dailyStatisticsList);

    /**
     * 批量更新汇总统计数据
     *
     * @param sumStatisticsList // 汇总统计列表
     * @return void             // 无返回
     */
    void updateSumData(List<SumStatistics> sumStatisticsList);

    /**
     * 查询项目日统计数据
     *
     * @param projectId             // 项目ID
     * @return List<DailyStatistics> // 日统计列表
     */
    List<DailyStatistics> getDailyDataByProject(String projectId);

    /**
     * 查询项目汇总统计数据
     *
     * @param projectId    // 项目ID
     * @return SumStatistics // 汇总统计实体
     */
    SumStatistics getSumDataByProject(String projectId);

    /**
     * 查询项目下用例总数
     *
     * @return List<StatisticsDTO> // 项目维度计数
     */
    List<StatisticsDTO> getCaseCountByProject();

    /**
     * 查询项目下今日新增用例数
     *
     * @return List<StatisticsDTO> // 项目维度计数  
     */
    List<StatisticsDTO> getCaseTodayNewCountByProject();

    /**
     * 查询项目下近一周新增用例数
     *
     * @return List<StatisticsDTO> // 项目维度计数  
     */
    List<StatisticsDTO> getCaseWeekNewCountByProject();

    /**
     * 查询项目下今日运行用例数
     *
     * @return List<StatisticsDTO> // 项目维度计数  
     */
    List<StatisticsDTO> getCaseTodayRunCountByProject();

    /**
     * 查询项目下累计运行用例数
     *
     * @return List<StatisticsDTO> // 项目维度计数  
     */
    List<StatisticsDTO> getCaseTotalRunCountByProject();

    /**
     * 查询项目下累计+今日运行用例数
     *
     * @return List<StatisticsDTO> // 项目维度计数  
     */
    List<StatisticsDTO> getCaseTotalTodayRunCountByProject();

    /**
     * 查询项目下测试计划运行排行榜（Top）
     *
     * @return List<StatisticsDTO> // 排行榜数据
     */
    List<StatisticsDTO> getPlanRunTopByProject();

    /**
     * 查询项目下用例失败排行榜（Top）
     *
     * @return List<StatisticsDTO> // 排行榜数据
     */
    List<StatisticsDTO> getCaseFailTopByProject();
}
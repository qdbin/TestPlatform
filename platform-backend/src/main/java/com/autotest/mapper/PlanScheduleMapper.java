package com.autotest.mapper;

import com.autotest.domain.PlanSchedule;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：测试计划调度配置
 * 用途：新增/更新调度配置、按计划ID查询、范围查询待运行的计划
 */
@Mapper
public interface PlanScheduleMapper {
    /**
     * 新增计划调度配置
     *
     *     @param planSchedule // 调度配置实体
     *     @return void        // 无返回
     */
    void addPlanSchedule(PlanSchedule planSchedule);

    /**
     * 更新计划调度配置
     *
     *     @param planSchedule // 调度配置实体
     *     @return void        // 无返回
     */
    void updatePlanSchedule(PlanSchedule planSchedule);

    /**
     * 查询计划的调度配置
     *
     *     @param planId          // 计划ID
     *     @return PlanSchedule   // 调度配置实体
     */
    PlanSchedule getPlanSchedule(String planId);

    /**
     * 查询待运行的计划调度列表（按下一次运行时间范围）
     *
     *     @param minNextRunTime // 最小下一次运行时间戳
     *     @param maxNextRunTime // 最大下一次运行时间戳
     *     @return List<PlanSchedule> // 调度列表
     */
    List<PlanSchedule> getToRunPlanScheduleList(Long minNextRunTime, Long maxNextRunTime);
}
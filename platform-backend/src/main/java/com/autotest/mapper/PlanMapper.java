package com.autotest.mapper;

import com.autotest.domain.Plan;
import com.autotest.dto.PlanDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：测试计划数据访问
 * 用途：计划新增/更新/删除、详情获取与分页列表查询
 */
@Mapper
public interface PlanMapper {
    /**
     * 新增测试计划
     *
     *     @param plan  // 计划实体
     *     @return void // 无返回
     */
    void addPlan(Plan plan);

    /**
     * 更新测试计划
     *
     *     @param plan  // 计划实体
     *     @return void // 无返回
     */
    void updatePlan(Plan plan);

    /**
     * 删除测试计划（逻辑删除/归档）
     *
     *     @param id    // 计划ID
     *     @return void // 无返回
     */
    void deletePlan(String id);

    /**
     * 获取测试计划详情
     *
     *     @param id       // 计划ID
     *     @return PlanDTO // 计划详情（含调度信息）
     */
    PlanDTO getPlanDetail(String id);

    /**
     * 分页查询测试计划列表
     *
     *     @param request         // 查询请求（分页/条件/项目）
     *     @return List<PlanDTO>  // 计划列表
     */
    List<PlanDTO> getPlanList(QueryRequest request);
}
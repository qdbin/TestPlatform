package com.autotest.mapper;

import com.autotest.domain.PlanNotice;
import org.apache.ibatis.annotations.Mapper;


/**
 * 映射：计划通知配置
 * 用途：新增/更新计划通知配置，按计划ID查询通知规则
 */
@Mapper
public interface PlanNoticeMapper {
    /**
     * 新增计划通知配置
     *
     *     @param planNotice // 计划通知实体
     *     @return void      // 无返回
     */
    void addPlanNotice(PlanNotice planNotice);

    /**
     * 更新计划通知配置
     *
     *     @param planNotice // 计划通知实体
     *     @return void      // 无返回
     */
    void updatePlanNotice(PlanNotice planNotice);

    /**
     * 按计划ID查询通知配置
     *
     *     @param planId     // 计划ID
     *     @return PlanNotice // 通知配置实体
     */
    PlanNotice getPlanNotice(String planId);
}
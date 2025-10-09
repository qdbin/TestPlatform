package com.autotest.mapper;

import com.autotest.domain.PlanCollection;
import com.autotest.dto.PlanCollectionDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * MyBatis Mapper：计划-集合关系
 * 负责计划与集合绑定关系的新增、删除、查询与统计
 */
@Mapper
public interface PlanCollectionMapper {
    /**
     * 批量新增计划-集合绑定
     * @param planCollections 计划-集合关系列表
     */
    void addPlanCollection(List<PlanCollection> planCollections);

    /**
     * 删除指定计划下的所有集合绑定
     * @param planId 计划ID
     */
    void deletePlanCollection(String planId);

    /**
     * 查询计划下的集合列表
     * @param planId 计划ID
     * @return 集合DTO列表
     */
    List<PlanCollectionDTO> getPlanCollectionList(String planId);

    /**
     * 统计计划下的用例数量
     * @param planId 计划ID
     * @return 用例数量
     */
    Integer getPlanCaseCount(String planId);
}
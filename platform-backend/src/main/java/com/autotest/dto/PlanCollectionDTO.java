package com.autotest.dto;

import com.autotest.domain.PlanCollection;
import lombok.Getter;
import lombok.Setter;

/**
 * 类型: DTO
 * 职责: 扩展测试计划集合实体的视图模型，补充集合名称与版本信息以便于报告统计与展示
 */
@Getter
@Setter
public class PlanCollectionDTO extends PlanCollection {
    private String collectionName; // 集合名称，用于测试计划与报告展示

    private String collectionVersion; // 集合版本名称，用于版本区分与统计
}

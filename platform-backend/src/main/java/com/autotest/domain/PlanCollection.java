package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: PlanCollection
 * 职责: 测试计划与集合的关联关系记录
 */
@Data
public class PlanCollection implements Serializable {
    private String id;           // 主键ID

    private String planId;       // 计划ID

    private String collectionId; // 集合ID

}
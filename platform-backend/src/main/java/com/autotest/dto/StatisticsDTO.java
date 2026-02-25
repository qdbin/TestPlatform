package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * 实体：统计信息载体
 * 用途：承载项目维度的数量统计与通过率
 */
@Getter
@Setter
public class StatisticsDTO {

    private String projectId; // 项目ID（统计归属）

    private String id;        // 主键ID/对象ID

    private String name;      // 名称（模块/集合/用例等）

    private Integer count;    // 总数量（样本数）

    private Integer pass;     // 通过数量

    private Float passRate;   // 通过率（0-100或0-1视使用处）

}

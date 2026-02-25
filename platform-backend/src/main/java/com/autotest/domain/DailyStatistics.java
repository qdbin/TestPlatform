package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：项目每日统计（date:project）
 * 用途：记录每日新增/累计/运行与通过率等数据
 */
@Data
public class DailyStatistics implements Serializable {
    private String id;                  // 主键ID

    private String statDate;            // 统计日期（yyyy-MM-dd）

    private String projectId;           // 项目ID

    private Integer apiCaseNew=0;       // 当天新增API用例数

    private Integer webCaseNew=0;       // 当天新增Web用例数

    private Integer appCaseNew=0;       // 当天新增App用例数

    private Integer apiCaseSum=0;       // 累计API用例数

    private Integer webCaseSum=0;       // 累计Web用例数

    private Integer appCaseSum=0;       // 累计App用例数

    private Integer apiCaseRun=0;       // 当天执行API用例数

    private Integer webCaseRun=0;       // 当天执行Web用例数

    private Integer appCaseRun=0;       // 当天执行App用例数

    private Float apiCasePassRate=0.0F; // API用例通过率

    private Float webCasePassRate=0.0F; // Web用例通过率

    private Float appCasePassRate=0.0F; // App用例通过率

}
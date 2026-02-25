package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：项目汇总统计（project:sum）
 * 用途：记录项目累计用例、近周新增、运行总量与Top信息
 */
@Data
public class SumStatistics implements Serializable {
    private String id;                // 主键ID

    private String projectId;         // 项目ID

    private Integer apiCaseTotal=0;   // 累计API用例数

    private Integer apiCaseNewWeek=0; // 近一周新增API用例数

    private Integer webCaseTotal=0;   // 累计Web用例数

    private Integer webCaseNewWeek=0; // 近一周新增Web用例数

    private Integer appCaseTotal=0;   // 累计App用例数

    private Integer appCaseNewWeek=0; // 近一周新增App用例数

    private Integer caseRunTotal=0;   // 累计用例运行总数

    private Integer caseRunToday=0;   // 今日用例运行数

    private String planRunWeekTop;    // 近周计划运行排行榜（JSON或逗号分隔）

    private String caseFailWeekTop;   // 近周用例失败排行榜（JSON或逗号分隔）

}
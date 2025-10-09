package com.autotest.common.constants;

/**
 * 枚举：报告来源类型
 * 用途：区分执行数据的来源（计划/集合/用例/临时调试）。
 */
public enum ReportSourceType {
    /** 计划执行，来源于计划任务 */
    PLAN("plan"),
    /** 集合执行，来源于接口集合 */
    COLLECTION("collection"),
    /** 用例执行，来源于单个用例 */
    CASE("case"),
    /** 临时调试任务，来源于 debug_data 临时表 */
    TEMP("temp");

    private final String value;
    ReportSourceType(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

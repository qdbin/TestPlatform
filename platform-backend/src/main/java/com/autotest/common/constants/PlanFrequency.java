package com.autotest.common.constants;

/**
 * 枚举：计划调度频率
 * 用途：统一表达定时计划的触发周期
 */
public enum PlanFrequency {
    ONLY_ONE("ONLY_ONE"),   // 仅一次
    HALF_HOUR("HALF_HOUR"), // 半小时
    ONE_HOUR("ONE_HOUR"),   // 一小时
    HALF_DAY("HALF_DAY"),   // 半天
    ONE_DAY("ONE_DAY"),     // 一天
    ONE_WEEK("ONE_WEEK"),   // 一周
    ONE_MONTH("ONE_MONTH"); // 一个月

    private final String value;
    PlanFrequency(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

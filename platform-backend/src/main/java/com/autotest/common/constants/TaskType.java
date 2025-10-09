package com.autotest.common.constants;

/**
 * 枚举：任务类型
 * 用途：区分任务优先级与来源（调试/手动/定时/外部调用）。
 * 说明：内置引擎调试优先级最高，其次是手动，再定时；自定义引擎默认按时间顺序。
 */
public enum TaskType {
    /** 用例调试或执行 */
    DEBUG("debug"),
    /** 集合或计划手动执行 */
    RUN("run"),
    /** 计划定时任务执行 */
    SCHEDULE("schedule"),
    /** 外部接口触发的计划外执行 */
    API("api");

    private final String value;
    TaskType(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

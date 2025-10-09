package com.autotest.common.constants;

/**
 * 枚举：引擎类型
 * 用途：区分平台默认系统引擎与自定义引擎
 */
public enum EngineType {
    SYSTEM("system"), // 系统引擎
    CUSTOM("custom"); // 自定义引擎

    private final String value;
    EngineType(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

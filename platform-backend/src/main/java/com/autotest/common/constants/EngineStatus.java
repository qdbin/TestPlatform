package com.autotest.common.constants;

/**
 * 常量：引擎状态枚举
 * 用途：统一表示引擎在线/离线/运行态
 */
public enum EngineStatus {
    OFFLINE("offline"), // 离线
    ONLINE("online"),   // 在线
    RUNNING("running"); // 运行中

    private final String value;

    EngineStatus(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

package com.autotest.common.constants;

/**
 * 枚举：设备状态
 * 用途：统一表示设备在线/占用/冷却/测试中等状态
 */
public enum DeviceStatus {
    OFFLINE("offline"),   // 离线
    ONLINE("online"),     // 在线
    USING("using"),       // 使用中（占用）
    COLDING("colding"),   // 冷却中
    TESTING("testing");   // 测试中

    private final String value;

    DeviceStatus(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

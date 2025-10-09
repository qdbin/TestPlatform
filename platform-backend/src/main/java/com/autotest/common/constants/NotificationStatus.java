package com.autotest.common.constants;

/**
 * 枚举：通知开关状态
 * 用途：统一表示通知的启用/禁用态
 */
public enum NotificationStatus {
    ENABLE("enable"),  // 启用
    DISABLE("disable"); // 禁用

    private final String value;

    NotificationStatus(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}

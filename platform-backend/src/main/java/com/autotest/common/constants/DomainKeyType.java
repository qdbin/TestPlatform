package com.autotest.common.constants;

/**
 * 枚举：域名匹配键类型
 * 用途：标识域名解析时使用的匹配方式（签名或路径）。
 */
public enum DomainKeyType {
    /** 签名匹配（如域名签名） */
    SIGN("sign"),
    /** 路径匹配（按请求路径规则） */
    PATH("path");

    /** 枚举值的字符串表示 */
    private final String value;

    DomainKeyType(String value) {
        this.value = value;
    }

    /**
     * 返回枚举对应的字符串值
     */
    @Override
    public String toString() {
        return this.value;
    }
}

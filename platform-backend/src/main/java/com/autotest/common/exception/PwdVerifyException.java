package com.autotest.common.exception;

/**
 * 类：密码校验异常
 * 职责：在登录或修改密码时旧密码校验失败抛出异常
 */
public class PwdVerifyException extends RuntimeException{
    /**
     * 构造：使用消息初始化异常
     *
     * @param message // 异常提示信息
     */
    public PwdVerifyException(String message) {
        super(message);
    }

    /**
     * 构造：使用原始异常包装
     *
     * @param t // 原始异常
     */
    private PwdVerifyException(Throwable t) {
        super(t);
    }

    /**
     * 工具：直接抛出密码校验异常
     *
     * @param message // 异常提示信息
     */
    public static void throwException(String message) {
        throw new PwdVerifyException(message);
    }

    /**
     * 工具：获取异常实例（实际行为为抛出异常）
     *
     * @param message // 异常提示信息
     * @return PwdVerifyException // 异常类型（说明用途）
     */
    public static PwdVerifyException getException(String message) {
        throw new PwdVerifyException(message);
    }

    /**
     * 工具：直接抛出包装异常
     *
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new PwdVerifyException(t);
    }

}

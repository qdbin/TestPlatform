package com.autotest.common.exception;

/**
 * 异常：登录校验失败
 * 用途：在登录鉴权过程中抛出账号/密码/验证码等校验异常
 */
public class LoginVerifyException extends RuntimeException{
    /**
     * 以消息构造异常
     *
     * @param message // 异常信息
     */
    public LoginVerifyException(String message) {
        super(message);
    }

    /**
     * 以原始异常构造（私有）
     *
     * @param t // 原始异常
     */
    private LoginVerifyException(Throwable t) {
        super(t);
    }

    /**
     * 直接抛出携带消息的异常
     *
     * @param message // 异常信息
     */
    public static void throwException(String message) {
        throw new LoginVerifyException(message);
    }

    /**
     * 获取携带消息的异常实例
     *
     * @param message // 异常信息
     * @return LoginVerifyException // 异常实例
     */
    public static LoginVerifyException getException(String message) {
        throw new LoginVerifyException(message);
    }

    /**
     * 直接抛出包装原始异常
     *
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new LoginVerifyException(t);
    }

}

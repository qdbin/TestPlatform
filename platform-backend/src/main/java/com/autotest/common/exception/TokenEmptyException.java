package com.autotest.common.exception;

/**
 * 异常：令牌缺失
 * 用途：当请求未携带或解析不到有效 Token 时抛出
 */
public class TokenEmptyException extends RuntimeException{
    /**
     * 以消息构造异常
     *
     * @param message // 异常信息
     */
    public TokenEmptyException(String message) {
        super(message);
    }

    /**
     * 以原始异常构造（私有）
     *
     * @param t // 原始异常
     */
    private TokenEmptyException(Throwable t) {
        super(t);
    }

    /**
     * 直接抛出携带消息的异常
     *
     * @param message // 异常信息
     */
    public static void throwException(String message) {
        throw new TokenEmptyException(message);
    }

    /**
     * 获取携带消息的异常实例
     *
     * @param message // 异常信息
     * @return TokenEmptyException // 异常实例
     */
    public static TokenEmptyException getException(String message) {
        throw new TokenEmptyException(message);
    }

    /**
     * 直接抛出包装原始异常
     *
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new TokenEmptyException(t);
    }

}

package com.autotest.common.exception;


/**
 * 异常：平台运行时异常封装
 * 用途：统一抛出与包装业务异常
 */
public class LMException extends RuntimeException{
    /**
     * 以消息构造异常
     *
     * @param message // 异常信息
     */
    public LMException(String message) {
        super(message);
    }

    /**
     * 以原始异常构造（私有）
     *
     * @param t // 原始异常
     */
    private LMException(Throwable t) {
        super(t);
    }

    /**
     * 直接抛出携带消息的异常
     *
     * @param message // 异常信息
     * @return void   // 直接抛出，无返回
     */
    public static void throwException(String message) {
        throw new LMException(message);
    }

    /**
     * 获取携带消息的异常实例
     *
     * @param message // 异常信息
     * @return LMException // 异常实例
     */
    public static LMException getException(String message) {
        throw new LMException(message);
    }

    /**
     * 直接抛出包装原始异常
     *
     * @param t // 原始异常
     * @return void // 直接抛出，无返回
     */
    public static void throwException(Throwable t) {
        throw new LMException(t);
    }

}

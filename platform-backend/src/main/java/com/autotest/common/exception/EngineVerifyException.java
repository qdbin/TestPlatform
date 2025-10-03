package com.autotest.common.exception;

/**
 * 类：引擎校验异常
 * 职责：在执行引擎鉴权/校验失败时抛出业务异常
 */
public class EngineVerifyException extends RuntimeException{
    /**
     * 构造：使用消息初始化异常
     *
     * @param message // 异常提示信息
     */
    public EngineVerifyException(String message) {
        super(message);
    }

    /**
     * 构造：使用原始异常包装
     *
     * @param t // 原始异常
     */
    private EngineVerifyException(Throwable t) {
        super(t);
    }

    /**
     * 工具：直接抛出引擎校验异常
     *
     * @param message // 异常提示信息
     */
    public static void throwException(String message) {
        throw new EngineVerifyException(message);
    }

    /**
     * 工具：获取异常实例（实际行为为抛出异常）
     *
     * @param message // 异常提示信息
     * @return EngineVerifyException // 异常类型（说明用途）
     */
    public static EngineVerifyException getException(String message) {
        throw new EngineVerifyException(message);
    }

    /**
     * 工具：直接抛出包装异常
     *
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new EngineVerifyException(t);
    }

}

package com.autotest.common.exception;

/**
 * 类：重复数据异常
 * 职责：在新增/更新等场景命中“唯一性”冲突时抛出业务异常
 */
public class DuplicateException extends RuntimeException{
    /**
     * 构造：使用消息初始化异常
     * @param message // 异常提示信息
     */
    public DuplicateException(String message) {
        super(message);
    }

    /**
     * 构造：使用原始异常包装
     * @param t // 原始异常
     */
    private DuplicateException(Throwable t) {
        super(t);
    }

    /**
     * 工具：直接抛出重复异常
     * @param message // 异常提示信息
     */
    public static void throwException(String message) {
        throw new DuplicateException(message);
    }

    /**
     * 工具：获取异常实例（实际行为为抛出异常）
     * @param message // 异常提示信息
     * @return DuplicateException // 异常类型（说明用途）
     */
    public static DuplicateException getException(String message) {
        throw new DuplicateException(message);
    }

    /**
     * 工具：直接抛出包装异常
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new DuplicateException(t);
    }

}

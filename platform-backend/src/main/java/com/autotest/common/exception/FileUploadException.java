package com.autotest.common.exception;

/**
 * 异常：文件上传失败
 * 用途：统一在文件上传过程出现错误时抛出或包装异常
 */
public class FileUploadException extends RuntimeException{
    /**
     * 以消息构造异常
     *
     * @param message // 异常信息
     */
    public FileUploadException(String message) {
        super(message);
    }

    /**
     * 以原始异常构造（私有）
     *
     * @param t // 原始异常
     */
    private FileUploadException(Throwable t) {
        super(t);
    }

    /**
     * 直接抛出携带消息的异常
     *
     * @param message // 异常信息
     */
    public static void throwException(String message) {
        throw new FileUploadException(message);
    }

    /**
     * 获取携带消息的异常实例（实际行为为抛出异常）
     *
     * @param message // 异常信息
     * @return FileUploadException // 异常类型（说明用途）
     */
    public static FileUploadException getException(String message) {
        throw new FileUploadException(message);
    }

    /**
     * 直接抛出包装原始异常
     *
     * @param t // 原始异常
     */
    public static void throwException(Throwable t) {
        throw new FileUploadException(t);
    }

}

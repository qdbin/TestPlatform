package com.autotest.common.response;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.exceptions.TokenExpiredException;
import com.autotest.common.constants.ResponseCode;
import com.autotest.common.exception.*;
import com.autotest.response.TemplateResponse;
import org.springframework.validation.ObjectError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 统一异常处理
 * 职责：捕获业务与鉴权相关异常，按平台响应规范包装为 TemplateResponse
 * 范围：控制层与拦截器抛出的常见异常（登录、权限、令牌、上传等）
 */
@RestControllerAdvice
public class ExceptionControllerAdvice {

    /**
     * 异常处理：平台运行时异常
     * 功能：将业务异常包装为统一失败响应
     * @param e // 平台业务异常
     * @return TemplateResponse<String> // 统一失败响应
     */
    @ExceptionHandler(LMException.class)
    public TemplateResponse<String> LMExceptionHandler(LMException e) {
        // 未知的失败
        return new TemplateResponse<>(ResponseCode.FAILED, e.getMessage());
    }

    /**
     * 异常处理：参数校验失败
     * 功能：提取首个校验错误信息并包装为校验失败响应
     * @param e // 参数校验异常
     * @return TemplateResponse<String> // 校验失败响应
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public TemplateResponse<String> MethodArgumentNotValidExceptionHandler(MethodArgumentNotValidException e) {
        ObjectError objectError = e.getBindingResult().getAllErrors().get(0);
        return new TemplateResponse<>(ResponseCode.VALIDATE_FAILED, objectError.getDefaultMessage());
    }

    /**
     * 异常处理：令牌校验失败
     * 功能：JWT 校验错误包装为 TOKEN_FAILED 响应
     * @param e // JWT 校验异常
     * @return TemplateResponse<String> // 令牌校验失败响应
     */
    @ExceptionHandler(JWTVerificationException.class)
    public TemplateResponse<String> TokenVerifyExceptionHandler(JWTVerificationException e) {
        return new TemplateResponse<>(ResponseCode.TOKEN_FAILED, e.getMessage());
    }

    /**
     * 异常处理：令牌过期
     * 功能：Token 过期异常包装为 TOKEN_EXPIRE 响应
     * @param e // Token 过期异常
     * @return TemplateResponse<String> // 令牌过期响应
     */
    @ExceptionHandler(TokenExpiredException.class)
    public TemplateResponse<String> TokenExpireExceptionHandler(TokenExpiredException e) {
        return new TemplateResponse<>(ResponseCode.TOKEN_EXPIRE, e.getMessage());
    }

    /**
     * 异常处理：令牌缺失
     * 功能：缺少 Token 时返回 TOKEN_EMPTY 响应
     * @param e // 令牌缺失异常
     * @return TemplateResponse<String> // 令牌缺失响应
     */
    @ExceptionHandler(TokenEmptyException.class)
    public TemplateResponse<String> NonLoginExceptionHandler(TokenEmptyException e) {
        return new TemplateResponse<>(ResponseCode.TOKEN_EMPTY, e.getMessage());
    }

    /**
     * 异常处理：登录校验失败
     * 功能：账号/密码等校验失败返回 LOGIN_FAILED 响应
     * @param e // 登录校验异常
     * @return TemplateResponse<String> // 登录失败响应
     */
    @ExceptionHandler(LoginVerifyException.class)
    public TemplateResponse<String> LoginVerifyExceptionHandler(LoginVerifyException e) {
        return new TemplateResponse<>(ResponseCode.LOGIN_FAILED, e.getMessage());
    }

    /**
     * 异常处理：内容重复
     * 功能：插入/更新重复内容返回 DUPLICATE_FAILED 响应
     * @param e // 重复内容异常
     * @return TemplateResponse<String> // 重复失败响应
     */
    @ExceptionHandler(DuplicateException.class)
    public TemplateResponse<String> DuplicateContentExceptionHandler(DuplicateException e) {
        return new TemplateResponse<>(ResponseCode.DUPLICATE_FAILED, e.getMessage());
    }

    /**
     * 异常处理：文件上传失败
     * 功能：上传过程错误返回 UPLOAD_FAILED 响应
     * @param e // 上传异常
     * @return TemplateResponse<String> // 上传失败响应
     */
    @ExceptionHandler(FileUploadException.class)
    public TemplateResponse<String> FileUploadExceptionHandler(FileUploadException e) {
        return new TemplateResponse<>(ResponseCode.UPLOAD_FAILED, e.getMessage());
    }

    /**
     * 异常处理：引擎校验失败
     * 功能：引擎鉴权逻辑异常返回 ENGINE_FAILED 响应
     * @param e // 引擎校验异常
     * @return TemplateResponse<String> // 引擎失败响应
     */
    @ExceptionHandler(EngineVerifyException.class)
    public TemplateResponse<String> EngineVerifyExceptionHandler(EngineVerifyException e) {
        return new TemplateResponse<>(ResponseCode.ENGINE_FAILED, e.getMessage());
    }

    /**
     * 异常处理：密码校验失败
     * 功能：密码强度/一致性校验失败返回 PASSWORD_FAILED 响应
     * @param e // 密码校验异常
     * @return TemplateResponse<String> // 密码失败响应
     */
    @ExceptionHandler(PwdVerifyException.class)
    public TemplateResponse<String> PasswordVerifyExceptionHandler(PwdVerifyException e) {
        return new TemplateResponse<>(ResponseCode.PASSWORD_FAILED, e.getMessage());
    }
}

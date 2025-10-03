package com.autotest.common.response;

import com.autotest.common.exception.LMException;
import com.autotest.response.TemplateResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.ByteArrayHttpMessageConverter;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

/**
 * 统一响应包装
 * 职责：对控制层返回值统一封装为 TemplateResponse；二进制与 String 类型特殊处理
 * 范围：生效于 com.autotest.controller 包下的所有控制器
 */
@RestControllerAdvice(basePackages = {"com.autotest.controller"})
public class ResponseControllerAdvice implements ResponseBodyAdvice<Object> {
    
    /**
     * 判断是否需要进行统一包装
     * @param returnType 控制器方法的返回类型信息
     * @param aClass     实际使用的消息转换器类型
     * @return boolean   是否进行包装（二进制类型不包装）
     */
    @Override
    public boolean supports(MethodParameter returnType, Class<? extends HttpMessageConverter<?>> aClass) {
        // 二进制（字节数组）响应直接透传，不做统一包装
        return !aClass.equals(ByteArrayHttpMessageConverter.class);
    }

    /**
     * 在响应体写出前统一处理返回值
     * @param data      控制器返回的数据
     * @param returnType 返回类型信息
     * @param mediaType  媒体类型
     * @param aClass     消息转换器类型
     * @param request    请求对象
     * @param response   响应对象
     * @return Object    包装后的返回对象或原始字符串
     */
    @Override
    public Object beforeBodyWrite(Object data, MethodParameter returnType, MediaType mediaType, Class<?
            extends HttpMessageConverter<?>> aClass, ServerHttpRequest request, ServerHttpResponse response) {
        // String 类型不能直接包装为对象，否则会被 StringHttpMessageConverter 直接作为字符串处理
        if (returnType.getGenericParameterType().equals(String.class)) {
            ObjectMapper objectMapper = new ObjectMapper(); // 构造 JSON 序列化器
            try {
                // 先将原始数据包装为 TemplateResponse，再序列化为 JSON 字符串
                return objectMapper.writeValueAsString(new TemplateResponse<>(data));
            } catch (JsonProcessingException e) {
                // String 类型序列化异常统一转为平台异常
                throw new LMException("String类型返回错误");
            }
        }
        // 非 String 类型：直接包装为 TemplateResponse 对象
        return new TemplateResponse<>(data);
    }
}
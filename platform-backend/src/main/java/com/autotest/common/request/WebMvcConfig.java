package com.autotest.common.request;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * 配置：WebMvc拦截链（LoginInterceptor）
 * 用途：注册登录与Token校验拦截器
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 注册登录与Token校验拦截器，匹配所有路径
        registry.addInterceptor(new LoginInterceptor()).addPathPatterns("/**");
    }
}

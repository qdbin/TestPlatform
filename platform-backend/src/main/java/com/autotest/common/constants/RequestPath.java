package com.autotest.common.constants;

/**
 * 常量：请求路径匹配（login:openapi）
 * 用途：登录与开放接口路径的正则匹配
 */
public enum RequestPath {
    
    LOGIN_PATH("^/autotest/login$"),                    // 登录接口
    REGISTER_PATH("^/autotest/register$"),              // 注册接口
    ENGINE_TOKEN_PATH("^/openapi/engine/token/apply$"), // 申请引擎Token
    SCREENSHOT_PATH("^/openapi/screenshot/.+$"),        // 图片预览
    DOWNLOAD_PATH("^/openapi/download/.+$"),            // 文件下载
    RUN_PATH("^/openapi/exec/.+$"),                     // 执行接口
    ENGINE_PATH("^/openapi/.+$"),                       // 引擎相关开放接口
    API_DOC("^/v3/.+$"),                                // api文档（json/yaml）
    SWAGGER_UI("^/swagger-ui/.+$");                     // swagger网页

    public String path;

    RequestPath(String path) {
        this.path = path;
    }

}

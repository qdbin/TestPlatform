package com.autotest.request;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：API请求载体（name:path）
 * 用途：承载接口定义与调试入参
 */
@Setter
@Getter
public class ApiRequest {
    private String id; // 主键ID

    private String name; // 接口名称

    private String level; // 优先级/级别

    private String moduleId; // 模块ID

    private String projectId; // 项目ID

    private String method; // HTTP方法

    private String path; // 请求路径

    private String protocol; // 协议（http/https）

    private String domainSign; // 域名签名/匹配标识

    private String description; // 描述说明

    private JSONArray header; // 请求头集合

    private JSONObject body; // 请求体

    private JSONArray query; // 查询参数

    private JSONArray rest; // REST路径参数

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private String status; // 状态标识
}

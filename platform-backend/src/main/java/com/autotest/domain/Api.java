package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：接口定义（name:path）
 * 用途：承载HTTP接口元数据与参数
 */
@Data
public class Api implements Serializable {
    private String id; // 主键ID

    private Long num; // 序号/编号

    private String name; // 接口名称

    private String level; // 优先级/级别

    private String moduleId; // 模块ID

    private String projectId; // 项目ID

    private String method; // HTTP方法

    private String path; // 请求路径

    private String protocol; // 协议（http/https）

    private String domainSign; // 域名签名/匹配标识

    private String description; // 描述说明

    private String header; // 请求头（JSON字符串）

    private String body; // 请求体（JSON字符串）

    private String query; // 查询参数（JSON字符串）

    private String rest; // REST路径参数（JSON字符串）

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private String status; // 状态标识

}
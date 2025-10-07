package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：接口用例步骤
 * 用途：描述API测试用例的单个步骤与断言、变量关联
 */
@Data
public class CaseApi implements Serializable {
    private String id;              // 步骤主键ID

    private Long index;             // 步骤序号（执行顺序）

    private String caseId;          // 所属用例ID

    private String apiId;           // 关联的接口ID

    private String description;     // 步骤描述

    private String header;          // 请求头（JSON字符串）

    private String body;            // 请求体（JSON/文本）

    private String query;           // 查询参数（key=value或JSON）

    private String rest;            // REST路径参数

    private String assertion;       // 断言规则（JSON）

    private String relation;        // 变量关联/提取规则

    private String controller;      // 控制器（条件/循环等流程控制）

}
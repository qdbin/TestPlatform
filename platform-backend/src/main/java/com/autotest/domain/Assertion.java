package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: Assertion
 * 职责: 断言元数据定义，描述断言名称等基础信息
 */
@Data
public class Assertion implements Serializable {
    private String id;    // 主键ID

    private String name;  // 断言名称

}
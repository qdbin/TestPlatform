package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：函数定义（Function）
 * 作用：承载平台内置/自定义函数的元数据，用于在用例、操作等场景中复用。
 * 维度：区分来源（系统/自定义）、入参、表达式/代码、归属项目及审计信息。
 */
@Data
public class Function implements Serializable {
    private String id;           // 主键ID（UUID）

    private String name;         // 函数名称（唯一，项目维度）

    private String from;         // 来源：system（系统）/ custom（自定义）

    private String param;        // 入参定义（JSON数组字符串）

    private String code;         // 函数代码内容（可选，脚本实现）

    private String expression;   // 函数字段表达式（可选，表达式实现）

    private String projectId;    // 归属项目ID（system来源可为空或全局）

    private String description;  // 描述信息（用途/备注）

    private Long createTime;     // 创建时间戳（ms）

    private Long updateTime;     // 更新时间戳（ms）

    private String createUser;   // 创建人ID

    private String updateUser;   // 更新人ID

    private Integer status;      // 状态：1有效/0删除
}
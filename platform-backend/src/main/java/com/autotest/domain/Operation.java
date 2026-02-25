package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：操作定义（name:type）
 * 用途：承载 Web/App 的通用操作元数据（元素、数据、代码等），
 *      支持按项目与系统维度复用与查询。
 */
@Data
public class Operation implements Serializable {
    private String id;           // 主键ID

    private String name;         // 操作名称

    private String type;         // 操作类型（参见 OperationType）

    private String uiType;       // UI类型（web/app）

    private String from;         // 来源（如组件/场景）

    private String system;       // 系统标识（App 场景下使用）

    private String element;      // 元素集合（JSON字符串）

    private String data;         // 数据集合（JSON字符串）

    private String code;         // 自定义代码脚本

    private String projectId;    // 所属项目ID

    private String description;  // 描述信息

    private Long createTime;     // 创建时间戳

    private Long updateTime;     // 更新时间戳

    private String createUser;   // 创建人ID

    private String updateUser;   // 更新人ID

    private Integer status;      // 状态（1正常/0删除）

}
package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：参数数据（ParamData）
    * 用途：参数组下的具体数据项与说明
    */
@Data
public class ParamData implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 数据名称

    private String paramData;     // 参数数据（JSON或文本）

    private String groupId;       // 所属参数分组ID

    private String dataType;      // 数据类型

    private String description;   // 数据描述

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

    private String createUser;    // 创建人

    private String updateUser;    // 更新人

    private Integer status;       // 状态（启用/禁用）

}
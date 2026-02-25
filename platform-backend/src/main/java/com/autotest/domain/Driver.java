package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：驱动配置（name:setting）
 * 用途：承载项目内的第三方驱动配置与描述
 */
@Data
public class Driver implements Serializable {
    private String id;            // 主键ID

    private String name;          // 驱动名称

    private String setting;       // 驱动设置（JSON字符串）

    private String description;   // 描述说明

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

}
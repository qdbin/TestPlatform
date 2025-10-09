package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：版本（name:description:projectId）
 * 用途：项目版本信息记录及创建/更新时间戳
 */
@Data
public class Version implements Serializable {
    private String id;            // 版本ID

    private String name;          // 版本名称

    private String description;   // 版本描述

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

}
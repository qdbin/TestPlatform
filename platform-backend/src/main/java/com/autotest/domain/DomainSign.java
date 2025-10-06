package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：域名标识（DomainSign）
    * 用途：项目内域名标识记录，含名称与描述
    */
@Data
public class DomainSign implements Serializable {
    private String id;            // 唯一标识ID

    private String name;          // 标识名称

    private String description;   // 标识描述信息

    private String projectId;     // 所属项目ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳
}
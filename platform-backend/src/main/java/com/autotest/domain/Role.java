package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：角色（id:name:projectId）
 * 用途：项目下角色定义与创建/更新时间戳管理
 */
@Data
public class Role implements Serializable {
    private String id;           // 角色ID

    private String name;         // 角色名称

    private String projectId;    // 所属项目ID

    private Long createTime;     // 创建时间戳

    private Long updateTime;     // 更新时间戳
}
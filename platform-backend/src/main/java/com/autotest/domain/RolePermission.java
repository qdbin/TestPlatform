package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：角色权限关系（RolePermission）
    * 用途：角色到权限的绑定关系记录
    */
@Data
public class RolePermission implements Serializable {
    private String id;            // 唯一标识ID

    private String roleId;        // 角色ID

    private String permissionId;  // 权限ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

}
package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
    * 实体：用户角色关系（UserRole）
    * 用途：用户在项目中的角色绑定记录
    */
@Data
public class UserRole implements Serializable {
    private String id;            // 唯一标识ID

    private String userId;        // 用户ID

    private String roleId;        // 角色ID

    private Long createTime;      // 创建时间戳

    private Long updateTime;      // 更新时间戳

}
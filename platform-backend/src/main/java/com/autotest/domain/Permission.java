package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：权限（id:name）
 * 用途：平台/项目权限编码与名称映射
 */
@Data
public class Permission implements Serializable {
    private String id;     // 权限编码ID

    private String name;   // 权限名称

}
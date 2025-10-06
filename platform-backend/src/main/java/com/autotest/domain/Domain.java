package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：域配置（type:key）
 * 用途：按环境维护域名/标识数据
 */
@Data
public class Domain implements Serializable {
    private String id; // 主键ID

    private String domainKeyType; // 匹配键类型（如path、host等）

    private String domainKey; // 匹配键值

    private String domainData; // 关联数据（如域名或替换值）

    private String environmentId; // 环境ID

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String createUser; // 创建人

    private String updateUser; // 更新人

    private Integer status; // 状态标识（启用/禁用）
}
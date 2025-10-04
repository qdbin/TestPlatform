package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：用户项目关系（userId:projectId）
 * 用途：记录用户与项目的绑定关系及时间戳
 */
@Data
public class UserProject implements Serializable {
    private String id;           // 关系ID

    private String userId;       // 用户ID

    private String projectId;    // 项目ID

    private Long createTime;     // 创建时间戳

    private Long updateTime;     // 更新时间戳

}
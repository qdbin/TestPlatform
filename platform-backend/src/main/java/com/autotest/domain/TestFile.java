package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: TestFile
 * 职责: 项目内测试文件元数据记录，用于文件上传与引用管理
 */
@Data
public class TestFile implements Serializable {
    private String id;              // 文件唯一ID

    private String name;            // 文件名称

    private String filePath;        // 存储路径或地址

    private String projectId;       // 所属项目ID

    private String description;     // 文件描述

    private Long createTime;        // 创建时间戳

    private Long updateTime;        // 更新时间戳

    private String createUser;      // 创建人ID

    private String updateUser;      // 更新人ID

    private Integer status;         // 状态标识

}
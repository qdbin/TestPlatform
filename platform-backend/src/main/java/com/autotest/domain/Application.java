package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：应用信息（name:appId）
 * 用途：承载移动/客户端应用的基础元数据
 */
@Data
public class Application implements Serializable {
    private String id; // 主键ID

    private String name; // 应用名称

    private String system; // 操作系统（Android/iOS等）

    private String appId; // 应用唯一标识（包名/BundleId）

    private String mainActivity; // 主入口Activity/页面

    private String description; // 描述信息

    private String projectId; // 所属项目ID

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

}
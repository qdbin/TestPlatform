package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：设备信息（serial:system）
 * 用途：承载测试设备属性与状态
 */
@Data
public class Device implements Serializable {
    private String id; // 主键ID

    private String serial; // 设备序列号

    private String name; // 设备名称

    private String system; // 操作系统（Android/iOS等）

    private String brand; // 品牌

    private String model; // 型号

    private String version; // 系统版本

    private String size; // 屏幕尺寸/分辨率

    private String sources; // 代理/来源信息（JSON）

    private String owner; // 所属人/占用者

    private String user;    // 设备使用者（用户ID或任务ID）

    private String agent; // 代理ID（心跳会话）

    private Integer timeout; // 使用超时阈值（秒）

    private String projectId; // 所属项目ID

    private Long createTime; // 创建时间戳

    private Long updateTime; // 更新时间戳

    private String status; // 状态（online/offline/running）

}
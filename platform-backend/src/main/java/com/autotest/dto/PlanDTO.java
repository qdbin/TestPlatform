package com.autotest.dto;

import com.autotest.domain.Plan;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
    * DTO：计划扩展视图（继承 Plan）
    * 用途：追加计划执行时间、频率、用户名、版本与环境名及集合
    */
@Getter
@Setter
public class PlanDTO extends Plan {

    private String startTime;             // 计划启动时间（可读格式）

    private String frequency;             // 计划执行频率描述

    private String username;              // 计划创建人/执行人用户名

    private String versionName;           // 关联版本名称

    private String environmentName;       // 关联环境名称

    private List<PlanCollectionDTO> planCollections; // 计划内集合列表

}

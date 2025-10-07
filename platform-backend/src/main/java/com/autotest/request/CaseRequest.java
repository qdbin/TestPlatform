package com.autotest.request;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 请求：用例基础信息与步骤集合
 * 用途：承载新建/更新用例时的基本元数据与步骤列表
 */

@Setter
@Getter
public class CaseRequest {
    private String id;                 // 用例ID

    private Long num;                  // 用例编号（序号）

    private String name;               // 用例名称

    private String level;              // 用例优先级/等级

    private String moduleId;           // 归属模块ID

    private String moduleName;         // 归属模块名称

    private String projectId;          // 项目ID（数据隔离）

    private String type;               // 用例类型（API/WEB/APP）

    private String thirdParty;         // 第三方标识/外部系统

    private String description;        // 用例描述

    private JSONArray environmentIds;  // 关联环境ID列表

    private String system;             // 系统类型（web/android/ios）

    private JSONObject commonParam;    // 通用参数（全局）

    private Long createTime;           // 创建时间戳

    private Long updateTime;           // 更新时间戳

    private String createUser;         // 创建人

    private String updateUser;         // 更新人

    private String status;             // 状态（正常/禁用等）

    private List<CaseApiRequest> caseApis;  // 接口型步骤列表

    private List<CaseWebRequest> caseWebs;  // Web型步骤列表

    private List<CaseAppRequest> caseApps;  // App型步骤列表
}

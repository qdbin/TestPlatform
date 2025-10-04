package com.autotest.request;

import com.alibaba.fastjson.JSONObject;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：通用查询请求（分页/过滤）
 * 用途：承载各模块列表查询的条件与过滤器
 */
@Setter
@Getter
public class QueryRequest {
    private String condition;   // 模糊查找输入值
    private String moduleId;    // 模块ID（筛选）
    private String createUser;  // 创建人（筛选）
    private String projectId;   // 项目ID（数据隔离）

    private String caseType;       // 用例类型（API/WEB/APP）
    private String collectionId;   // 报告所属集合ID（筛选）
    private String planId;         // 报告所属计划ID（筛选）
    private String operationType;  // 控件/操作类型（筛选）
    private String roleId;         // 角色ID（筛选角色用户列表）
    private String requestUser;    // 请求人（上下文标识）
    private String uiType;         // UI类型（web/app）
    private String system;         // 系统类型（android/apple）
    private String status;         // 设备状态（online/offline/using等）
    private JSONObject filter;     // 设备查询条件（复合过滤器）
}

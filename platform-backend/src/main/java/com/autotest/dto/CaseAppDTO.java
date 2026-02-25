package com.autotest.dto;

import com.autotest.domain.CaseApp;
import lombok.Getter;
import lombok.Setter;

/**
 * 类型: DTO
 * 职责: 扩展用例(App)实体的视图模型，补充操作名称与类型便于前端展示与业务处理
 */
@Getter
@Setter
public class CaseAppDTO extends CaseApp {

    private String operationName; // 操作名称，用于展示与日志描述

    private String operationType; // 操作类型（如点击、输入等），用于执行器识别

}

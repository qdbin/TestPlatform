package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * DTO：接口参数规则定义
 * 用途：描述生成校验用例的规则，包括参数名、类型、必填性与边界值定义。
 */
@Getter
@Setter
public class ApiParamRuleDTO{
    private String name;    // 参数名称

    private String type;    // 参数类型（String/Number/Boolean/SpecialStr等）

    private String required;    // 必填性规则（None/Required/Optional等）

    private String random;  // 边界值规则（与type配合使用）

    private String value; // 默认值（非校验场景或初始填充）
}

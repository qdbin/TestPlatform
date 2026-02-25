package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;

/**
 * DTO：接口参数校验项
 * 用途：描述针对单个参数的校验用例，包括校验方向（正向/逆向）、
 *      是否删除该参数、类型、说明与实际校验值。
 */
@Getter
@Setter
public class ApiParamVerifyDTO {

    private String name; // 参数名称

    private String direction; // 校验方向（正向/逆向）

    private Boolean delete=false; // 是否删除该参数（默认false）

    private String type; // 参数类型（String/Number/Boolean等）

    private String description; // 校验说明（用于报告展示）

    private Object value; // 校验使用的值（类型与type对应）
}

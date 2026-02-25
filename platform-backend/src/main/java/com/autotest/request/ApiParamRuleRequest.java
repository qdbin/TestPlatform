package com.autotest.request;

import com.alibaba.fastjson.JSONArray;
import com.autotest.dto.ApiParamRuleDTO;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：接口参数规则请求
 * 用途：承载接口各位置参数的校验规则及断言
 */
@Setter
@Getter
public class ApiParamRuleRequest {

    private String apiId;                      // 接口ID

    private List<ApiParamRuleDTO> header;      // 请求头参数规则

    private List<ApiParamRuleDTO>  body;       // 请求体参数规则

    private List<ApiParamRuleDTO>  query;      // 查询参数规则

    private List<ApiParamRuleDTO>  rest;       // REST路径参数规则

    private JSONArray  positiveAssertion;      // 正向断言

    private JSONArray  oppositeAssertion;      // 反向断言

    private String createUser;                 // 规则创建人
}

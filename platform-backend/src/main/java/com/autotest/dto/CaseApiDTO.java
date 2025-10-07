package com.autotest.dto;

import com.autotest.domain.CaseApi;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：接口用例步骤扩展DTO（继承 CaseApi）
 * 用途：承载API定义的展示字段（名称/路径/方法/协议/域标识）
 */
@Getter
@Setter
public class CaseApiDTO extends CaseApi {
    private String apiName;        // 接口名称

    private String apiPath;        // 接口路径

    private String apiMethod;      // HTTP方法

    private String apiProtocol;    // 协议（http/https）

    private String apiDomainSign;  // 域名签名（域标识）
}

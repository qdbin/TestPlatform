package com.autotest.dto;

import com.autotest.domain.Domain;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：域名扩展视图（继承 Domain）
 * 用途：追加域名签名名称等展示字段
 */


@Getter
@Setter
public class DomainDTO extends Domain {

    private String DomainSignName; // 域名签名名称（展示）

}

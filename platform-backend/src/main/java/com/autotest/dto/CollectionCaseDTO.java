package com.autotest.dto;

import com.autotest.domain.CollectionCase;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：集合-用例扩展DTO
 * 用途：承载集合中的用例展示属性
 */
@Getter
@Setter
public class CollectionCaseDTO extends CollectionCase {
    private String caseName;    // 用例名称

    private String caseModule;  // 用例所属模块名称

    private String caseType;    // 用例类型

    private String caseSystem;  // 系统标识（android/apple）
}

package com.autotest.dto;

import com.autotest.domain.CaseWeb;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：Web用例步骤扩展DTO（继承 CaseWeb）
 * 用途：承载Web操作步骤的展示字段
 */
@Getter
@Setter
public class CaseWebDTO extends CaseWeb {

    private String operationName; // 操作名称

    private String operationType; // 操作类型

}

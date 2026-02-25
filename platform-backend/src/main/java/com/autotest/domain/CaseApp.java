package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 实体：APP用例步骤
 * 用途：描述移动端自动化步骤（操作、元素、数据）
 */
@Data
public class CaseApp implements Serializable {
    private String id;           // 步骤主键ID

    private Long index;          // 步骤序号（执行顺序）

    private String caseId;       // 所属用例ID

    private String operationId;  // 操作ID（点击、输入、滑动等）

    private String description;  // 步骤描述

    private String element;      // 元素定位信息（JSON）

    private String data;         // 输入/断言数据（JSON/文本）

}
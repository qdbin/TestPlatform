package com.autotest.dto;

import com.autotest.domain.Case;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：用例扩展DTO（继承 Case）
 * 用途：承载用例的展示附加字段与分类型步骤列表
 */
@Getter
@Setter
public class CaseDTO extends Case {
    private String moduleName;             // 归属模块名称

    private String username;               // 创建人用户名

    private List<CaseApiDTO> caseApis;     // 接口型用例步骤列表

    private List<CaseWebDTO> caseWebs;     // Web型用例步骤列表

    private List<CaseAppDTO> caseApps;     // App型用例步骤列表
}

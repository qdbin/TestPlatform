package com.autotest.dto;

import com.autotest.domain.Element;
import lombok.Getter;
import lombok.Setter;

/**
 * 类型: DTO
 * 职责: 扩展页面元素实体的视图模型，补充所属模块与维护人信息，便于管理与展示
 */
@Getter
@Setter
public class ElementDTO extends Element {
    private String moduleName; // 元素所属模块名称，用于分组与筛选

    private String username; // 元素维护人用户名，用于显示责任归属
}

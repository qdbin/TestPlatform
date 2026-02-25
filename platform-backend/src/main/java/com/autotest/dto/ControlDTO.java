package com.autotest.dto;

import com.autotest.domain.Control;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：控件元素扩展视图（继承 Control）
 * 用途：在控件基础信息上，追加模块名称与用户名等展示字段。
 */
@Getter
@Setter
public class ControlDTO extends Control {
    /** 模块名称（所属模块的可读名称） */
    private String moduleName;

    /** 用户名称（创建或更新操作者的展示名称） */
    private String username;
}

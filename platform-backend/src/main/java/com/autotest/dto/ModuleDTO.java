package com.autotest.dto;

import com.autotest.domain.Module;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：模块扩展DTO
 * 用途：承载树结构与展示属性
 */
@Getter
@Setter
public class ModuleDTO extends Module {
    private List<ModuleDTO> children; // 子节点列表

    private String label;             // 展示标签（=name）

    private String moduleType;        // 模块类型标识
}

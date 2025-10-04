package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * DTO：导航菜单节点
 * 用途：承载前端导航菜单的数据结构，支持树形嵌套展示。
 */
@Getter
@Setter
public class MenuDTO {
    private Integer id;         // 菜单ID

    private String name;        // 菜单名称

    private String icon;        // 图标标识

    private String path;        // 路由路径

    private List<MenuDTO> menus; // 子菜单列表（树形）

}

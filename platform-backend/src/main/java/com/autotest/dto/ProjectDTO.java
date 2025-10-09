package com.autotest.dto;

import com.autotest.domain.Project;
import lombok.Getter;
import lombok.Setter;

/**
 * 类：项目DTO（扩展Project）
 * 职责：追加用户名等展示字段，用于项目列表/详情等场景
 */
@Getter
@Setter
public class ProjectDTO extends Project {

    private String username; // 用户名（通常为项目管理员或创建人）

}

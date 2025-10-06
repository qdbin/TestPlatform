package com.autotest.dto;

import com.autotest.domain.Environment;
import lombok.Getter;
import lombok.Setter;

/**
 * 类：环境DTO（扩展Environment）
 * 职责：追加用户名等附加字段，用于环境列表/详情展示
 */
@Getter
@Setter
public class EnvironmentDTO extends Environment {

    private String username; // 用户名（环境创建/维护者）

}

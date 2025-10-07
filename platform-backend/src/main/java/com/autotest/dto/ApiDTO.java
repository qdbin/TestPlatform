package com.autotest.dto;

import com.autotest.domain.Api;

import lombok.Getter;
import lombok.Setter;

/**
 * 实体：API传输对象（继承:Api）
 * 扩展：moduleName、username
 */
@Getter
@Setter
public class ApiDTO extends Api {
    private String moduleName; // 模块名称（展示用）

    private String username; // 创建/维护人名称
}

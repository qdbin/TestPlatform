package com.autotest.dto;

import com.autotest.domain.Function;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：函数扩展视图（继承 Function）
 * 用途：在查询函数列表时追加展示字段，如创建人名称。
 */
@Getter
@Setter
public class FunctionDTO extends Function {

    private String username; // 创建人用户名（展示用）
}

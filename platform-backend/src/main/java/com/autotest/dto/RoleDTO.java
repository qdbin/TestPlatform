package com.autotest.dto;

import com.autotest.domain.Role;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：角色扩展视图（继承 Role）
 * 用途：追加项目名称用于列表/详情展示
 */
@Getter
@Setter
public class RoleDTO extends Role {

    private String projectName; // 所属项目名称（展示）

}

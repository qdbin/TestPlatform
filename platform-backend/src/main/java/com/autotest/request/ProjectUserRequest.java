package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 请求：项目成员与角色维护
 * 用途：新增/编辑项目下的成员及关联角色集合
 */
@Setter
@Getter
public class ProjectUserRequest {
    /*
     * 是否覆盖式更新角色：
     * true  -> 将用户在项目下的角色同步为给定集合（新增缺失并删除多余）
     * false -> 仅追加给定角色（保留已有角色，不做删除）
     */
    private Boolean isEdit;

    // 项目ID：要维护成员/角色的项目标识
    private String projectId;

    // 用户ID列表：要添加或更新到项目下的用户集合
    private List<String> userIds;

    // 角色ID列表：为上述用户绑定的角色集合（可按需关联）
    private List<String> roleIds;
}

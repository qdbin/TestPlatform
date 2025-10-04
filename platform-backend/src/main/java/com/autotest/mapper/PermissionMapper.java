package com.autotest.mapper;

import com.autotest.domain.RolePermission;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：权限数据访问（角色权限/用户权限）
 * 用途：批量维护角色权限并按项目查询用户权限
 */
@Mapper
public interface PermissionMapper {

    /**
     * 批量新增角色权限绑定
     *
     * @param rolePermissions   // 角色权限列表（roleId-permissionId映射）
     * @return void             // 无返回
     *
     * 示例：传入3条绑定记录以一次性建立角色权限关系
     */
    void addRolePermission(List<RolePermission> rolePermissions);

    /**
     * 查询用户在指定项目下的权限编码列表
     *
     * @param projectId     // 项目ID
     * @param userId        // 用户ID
     * @return List<String> // 权限编码集合
     *
     * 说明：结合用户角色与项目内授权，返回可用权限码
     */
    List<String> getUserPermissionByProject(String projectId, String userId);
}
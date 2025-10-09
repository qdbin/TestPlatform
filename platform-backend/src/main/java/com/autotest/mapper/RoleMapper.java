package com.autotest.mapper;

import com.autotest.domain.Role;
import com.autotest.domain.RolePermission;
import com.autotest.domain.User;
import com.autotest.domain.UserRole;
import com.autotest.dto.RoleDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：角色数据访问（角色/成员/权限）
 * 用途：角色基础信息、成员绑定与权限分配维护
 */
@Mapper
public interface RoleMapper {

    /**
     * 按项目与名称查询角色
     *
     * @param projectId   // 项目ID
     * @param name        // 角色名称
     * @return Role       // 角色实体
     */
    Role getRoleByProjectAndName(String projectId, String name);

    /**
     * 查询角色-用户关系
     *
     * @param roleId     // 角色ID
     * @param userId     // 用户ID
     * @return UserRole  // 角色用户关系实体
     */
    UserRole getRoleUser(String roleId, String userId);

    /**
     * 新增角色成员绑定
     *
     * @param userRole   // 角色用户关系实体
     * @return void      // 无返回
     */
    void addRoleUser(UserRole userRole);

    /**
     * 批量新增角色
     *
     * @param roles    // 角色列表
     * @return void    // 无返回
     */
    void addRoles(List<Role> roles);

    /**
     * 批量新增角色权限绑定
     *
     * @param rolePermissions   // 角色权限映射列表
     * @return void             // 无返回
     */
    void addRolePermissions(List<RolePermission> rolePermissions);

    /**
     * 分页/条件查询角色列表
     *
     * @param queryRequest     // 查询载体（projectId/condition/page）
     * @return List<RoleDTO>   // 角色列表
     */
    List<RoleDTO> getRoleList(QueryRequest queryRequest);

    /**
     * 分页/条件查询角色成员
     *
     * @param queryRequest   // 查询载体（roleId/condition/page）
     * @return List<User>    // 用户列表
     */
    List<User> getRoleUserList(QueryRequest queryRequest);

    /**
     * 删除角色成员绑定
     *
     * @param roleId    // 角色ID
     * @param userId    // 用户ID
     * @return void     // 无返回
     */
    void deleteRoleUser(String roleId, String userId);
}
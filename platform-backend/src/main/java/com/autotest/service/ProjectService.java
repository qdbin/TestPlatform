package com.autotest.service;

import com.autotest.common.constants.PermissionEnum;
import com.autotest.common.exception.LMException;
import com.autotest.domain.*;
import com.autotest.mapper.CommonParamMapper;
import com.autotest.mapper.ProjectMapper;
import com.autotest.mapper.RoleMapper;
import com.autotest.mapper.UserMapper;
import com.autotest.dto.ProjectDTO;
import com.autotest.request.ProjectUserRequest;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 服务：项目业务处理（查询、创建、成员）
 * 职责：项目基础信息维护、角色权限初始化与成员绑定
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ProjectService {

    @Resource
    private ProjectMapper projectMapper;

    @Resource
    private RoleMapper roleMapper;

    @Resource
    private CommonParamMapper commonParamMapper;

    @Resource
    private UserMapper userMapper;

    /**
     * 查询用户所属项目列表
     *
     * @param userId           // 用户ID
     * @return List<Project>   // 项目列表
     */
    public List<Project> getUserProject(String userId) {
        return projectMapper.getUserProject(userId);
    }

    /**
     * 获取项目基础信息
     *
     * @param projectId   // 项目ID
     * @return Project    // 项目实体
     */
    public Project getProjectInfo(String projectId) {
        return projectMapper.getProjectById(projectId);
    }

    /**
     * 分页查询项目列表（支持名称模糊匹配）
     *
     * @param request            // 查询请求，包含分页与 condition
     * @return List<ProjectDTO>  // 项目列表数据
     */
    public List<ProjectDTO> getProjectList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return projectMapper.getProjectList(request);
    }

    /**
     * 分页查询项目成员列表（支持名称模糊匹配）
     *
     * @param request       // 查询请求，包含分页与 condition
     * @return List<User>   // 用户列表
     */
    public List<User> getProjectUserList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return projectMapper.getProjectUserList(request);
    }

    /**
     * 查询项目下的角色列表
     *
     * @param projectId   // 项目ID
     * @return List<Role> // 角色列表
     */
    public List<Role> getProjectRoleList(String projectId) {
        return projectMapper.getProjectRoleList(projectId);
    }

    /**
     * 保存新项目并进行初始化配置（角色、权限、成员、公共参数组）
     *
     * @param project // 项目实体（包含名称、管理员等）
     * @return void   // 无返回；重名抛出异常
     */
    public void saveProject(Project project){
        Project oldProject = projectMapper.getProjectByName(project.getName());
        if(oldProject != null){
            throw new LMException("项目重名");
        }

        // 新增项目
        project.setId(UUID.randomUUID().toString());
        project.setCreateTime(System.currentTimeMillis());
        project.setUpdateTime(System.currentTimeMillis());
        project.setStatus("Normal");
        projectMapper.addProject(project);

        // 新增项目角色（管理员、普通用户）
        List<Role> roles = new ArrayList<>();
        List<String> roleNames = new ArrayList<>();
        roleNames.add("项目管理员");
        roleNames.add("项目普通用户");
        for(String roleName:roleNames){
            Role role = new Role();
            role.setId(UUID.randomUUID().toString());
            role.setName(roleName);
            role.setProjectId(project.getId());
            role.setCreateTime(System.currentTimeMillis());
            role.setUpdateTime(System.currentTimeMillis());
            roles.add(role);
        }
        roleMapper.addRoles(roles);

        // 新增项目角色权限（一个角色有多个菜单权限）
        List<RolePermission> rolePermissions = new ArrayList<>();
        for(PermissionEnum permissionEnum: PermissionEnum.values()){
            if(permissionEnum != PermissionEnum.PROJECT_MENU){
                // 角色权限-admin（一个角色由多个权限）
                RolePermission adminRolePermission = new RolePermission();
                adminRolePermission.setId(UUID.randomUUID().toString());
                adminRolePermission.setCreateTime(System.currentTimeMillis());
                adminRolePermission.setUpdateTime(System.currentTimeMillis());
                adminRolePermission.setPermissionId(permissionEnum.id);
                if(permissionEnum == PermissionEnum.NORMAL_MENU || permissionEnum == PermissionEnum.SETTING_MENU){
                    // 角色权限-user（）
                    RolePermission commonRolePermission = new RolePermission();
                    commonRolePermission.setId(UUID.randomUUID().toString());
                    commonRolePermission.setCreateTime(System.currentTimeMillis());
                    commonRolePermission.setUpdateTime(System.currentTimeMillis());
                    commonRolePermission.setPermissionId(permissionEnum.id);
                    commonRolePermission.setRoleId(roles.get(1).getId());
                    rolePermissions.add(commonRolePermission);
                }
                adminRolePermission.setRoleId(roles.get(0).getId());
                rolePermissions.add(adminRolePermission);
            }
        }
        roleMapper.addRolePermissions(rolePermissions);

        // 新增用户角色
        UserRole userRole = new UserRole();
        userRole.setId(UUID.randomUUID().toString());
        userRole.setUserId(project.getProjectAdmin());
        userRole.setRoleId(roles.get(0).getId());   // 分配管理员角色
        userRole.setCreateTime(System.currentTimeMillis());
        userRole.setUpdateTime(System.currentTimeMillis());
        roleMapper.addRoleUser(userRole);

        // 新增用户项目
        UserProject userProject = new UserProject();
        userProject.setId(UUID.randomUUID().toString());
        userProject.setUserId(project.getProjectAdmin());
        userProject.setProjectId(project.getId());
        userProject.setCreateTime(System.currentTimeMillis());
        userProject.setUpdateTime(System.currentTimeMillis());
        projectMapper.addProjectUser(userProject);

        // 新增公共参数组
        List<ParamGroup> paramGroups = new ArrayList<>();
        paramGroups.add(this.getParamGroup(project.getId(), "Header", "接口请求头参数组", "system"));
        paramGroups.add(this.getParamGroup(project.getId(), "Proxy", "接口请求代理参数组", "system"));
        paramGroups.add(this.getParamGroup(project.getId(), "Custom", "自定义参数组", "custom"));
        commonParamMapper.insertParamGroup(paramGroups);
    }

    /**
     * 组装公共参数组实体
     *
     * @param projectId   // 项目ID
     * @param name        // 参数组名称
     * @param desc        // 参数组描述
     * @param type        // 参数组类型（system/custom）
     * @return ParamGroup // 参数组实体
     */
    private ParamGroup getParamGroup(String projectId, String name, String desc, String type){
        ParamGroup paramGroup = new ParamGroup();
        paramGroup.setId(UUID.randomUUID().toString());
        paramGroup.setProjectId(projectId);
        paramGroup.setName(name);
        paramGroup.setDescription(desc);
        paramGroup.setParamType(type);
        paramGroup.setCreateTime(System.currentTimeMillis());
        paramGroup.setUpdateTime(System.currentTimeMillis());
        paramGroup.setCreateUser("system_admin_user");
        paramGroup.setUpdateUser("system_admin_user");
        return paramGroup;
    }

    /**
     * 新增或编辑项目成员及其角色绑定关系
     *
     * @param request // 请求载体：projectId、userIds、roleIds、isEdit
     * @return void   // 无返回
     */
    public void saveProjectUser(ProjectUserRequest request){
        for(String userId: request.getUserIds()){
            // 若当前user与project没有绑定关系，则添加绑定
            if(projectMapper.getProjectUser(request.getProjectId(), userId) == null){
                UserProject userProject = new UserProject();
                userProject.setId(UUID.randomUUID().toString());
                userProject.setUserId(userId);
                userProject.setProjectId(request.getProjectId());
                userProject.setCreateTime(System.currentTimeMillis());
                userProject.setUpdateTime(System.currentTimeMillis());
                projectMapper.addProjectUser(userProject);  // 新增项目用户
            }

            // 仅追加，即对未绑定关系的进行追加绑定关系（edit==false）
            if(!request.getIsEdit()) {  // 新增项目用户
                for (String roleId : request.getRoleIds()) {
                    // 若已有绑定关系，则跳过
                    if (roleMapper.getRoleUser(roleId, userId) != null) {
                        continue;
                    }
                    UserRole userRole = new UserRole();
                    userRole.setId(UUID.randomUUID().toString());
                    userRole.setUserId(userId);
                    userRole.setRoleId(roleId);
                    userRole.setCreateTime(System.currentTimeMillis());
                    userRole.setUpdateTime(System.currentTimeMillis());
                    roleMapper.addRoleUser(userRole);   // 新增项目用户角色
                }
            }

            // 强制覆盖同步（edit==true）
            else {
                // 获得当前user的project_role
                List<String> oldRoleIds = userMapper.getUserRoleList(request.getProjectId(), userId);
                // 遍历project_role(最多两种角色-管理、普通)
                for(String newRoleId: request.getRoleIds()){
                    // 若该用户已有新指定的project_role则跳过，即已有的用户角色不做更改
                    if(oldRoleIds.contains(newRoleId)){
                        oldRoleIds.remove(newRoleId);
                        continue;
                    }
                    // 若该用户没有当前指定的角色则添加
                    UserRole userRole = new UserRole();
                    userRole.setId(UUID.randomUUID().toString());
                    userRole.setUserId(userId);
                    userRole.setRoleId(newRoleId);
                    userRole.setCreateTime(System.currentTimeMillis());
                    userRole.setUpdateTime(System.currentTimeMillis());
                    roleMapper.addRoleUser(userRole);   // 新增项目用户角色
                }
                // 删除该用户的未指定的角色
                for(String oldRoleId: oldRoleIds){
                    roleMapper.deleteRoleUser(oldRoleId, userId);
                }
            }
        }
    }

    /**
     * 删除项目成员及其角色关系
     *
     * @param projectId // 项目ID
     * @param userId    // 用户ID
     * @return void     // 无返回
     */
    public void deleteProjectUser(String projectId, String userId){
        projectMapper.deleteProjectUser(projectId, userId); // 删除项目用户
        List<String> roleIds = userMapper.getUserRoleList(projectId, userId);
        for(String roleId: roleIds){
            roleMapper.deleteRoleUser(roleId, userId);   // 删除项目角色
        }
    }

    /**
     * 删除项目（软删除，置状态为Delete）
     *
     * @param projectId // 项目ID
     * @return void     // 无返回
     */
    public void deleteProject(String projectId){
        projectMapper.deleteProject(projectId);
    }

    /**
     * 恢复项目（状态改回Normal）
     *
     * @param projectId // 项目ID
     * @return void     // 无返回
     */
    public void recoverProject(String projectId){
        projectMapper.recoverProject(projectId);
    }

}

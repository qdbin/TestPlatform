package com.autotest.mapper;

import com.autotest.domain.Project;
import com.autotest.domain.Role;
import com.autotest.domain.User;
import com.autotest.domain.UserProject;
import com.autotest.dto.ProjectDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：项目数据访问（项目/用户/角色）
 * 用途：项目基础信息、成员关系与角色权限维护
 */
@Mapper
public interface ProjectMapper {
    /**
     * 查询用户所属项目列表
     *
     * @param userId           // 用户ID
     * @return List<Project>   // 项目列表
     */
    List<Project> getUserProject(String userId);

    /**
     * 分页/条件查询项目列表
     *
     * @param request             // 查询条件载体（condition/page等）
     * @return List<ProjectDTO>   // 项目列表（含管理员等信息）
     */
    List<ProjectDTO> getProjectList(QueryRequest request);

    /**
     * 分页/条件查询项目成员
     *
     * @param request         // 查询条件载体（projectId/condition）
     * @return List<User>     // 用户列表
     */
    List<User> getProjectUserList(QueryRequest request);

    /**
     * 查询项目角色列表
     *
     * @param projectId      // 项目ID
     * @return List<Role>    // 角色列表
     */
    List<Role> getProjectRoleList(String projectId);

    /**
     * 查询所有项目ID
     *
     * @return List<String>  // 项目ID列表
     */
    List<String> getAllProjectId();

    /**
     * 通过名称查询项目
     *
     * @param name       // 项目名称
     * @return Project   // 项目实体
     */
    Project getProjectByName(String name);

    /**
     * 通过ID查询项目
     *
     * @param id         // 项目ID
     * @return Project   // 项目实体
     */
    Project getProjectById(String id);

    /**
     * 查询项目用户关系
     *
     * @param projectId       // 项目ID
     * @param userId          // 用户ID
     * @return UserProject    // 项目-用户关系实体
     */
    UserProject getProjectUser(String projectId, String userId);

    /**
     * 新增项目用户关系
     *
     * @param userProject    // 项目-用户关系实体
     * @return void          // 无返回
     */
    void addProjectUser(UserProject userProject);

    /**
     * 新增项目
     *
     * @param project    // 项目实体
     * @return void      // 无返回
     */
    void addProject(Project project);

    /**
     * 删除项目用户关系
     *
     * @param projectId   // 项目ID
     * @param userId      // 用户ID
     * @return void       // 无返回
     */
    void deleteProjectUser(String projectId, String userId);

    /**
     * 归档/删除项目
     *
     * @param id      // 项目ID
     * @return void   // 无返回
     */
    void deleteProject(String id);

    /**
     * 恢复项目
     *
     * @param id      // 项目ID
     * @return void   // 无返回
     */
    void recoverProject(String id);
}
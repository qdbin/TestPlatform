package com.autotest.mapper;

import com.autotest.domain.User;
import com.autotest.dto.UserDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：用户数据访问（查询/更新/新增）
 * 用途：用户信息、角色、密码与项目关系维护
 */
@Mapper
public interface UserMapper {
    /**
     * 查询用户详情
     *
     * @param id        // 用户ID
     * @return UserDTO  // 用户详情信息
     */
    UserDTO getUserInfo(String id);

    /**
     * 通过账号查询用户
     *
     * @param account   // 登录账号
     * @return UserDTO  // 用户信息
     */
    UserDTO getUser(String account);

    /**
     * 查询所有用户
     *
     * @return List<User> // 用户列表
     */
    List<User> getAllUser();

    /**
     * 模糊查询用户
     *
     * @param account   // 账号（模糊条件）
     * @return List<User> // 用户列表
     */
    List<User> queryUser(String account);

    /**
     * 查询用户在项目下的角色列表
     *
     * @param projectId // 项目ID
     * @param userId    // 用户ID
     * @return List<String> // 角色名称列表
     */
    List<String> getUserRoleList(String projectId, String userId);

    /**
     * 更新用户所属项目
     *
     * @param id         // 用户ID
     * @param projectId  // 项目ID
     * @return void      // 无返回
     */
    void updateProject(String id, String projectId);

    /**
     * 更新用户密码
     *
     * @param id        // 用户ID
     * @param password  // 新密码
     * @return void     // 无返回
     */
    void updatePassword(String id, String password);

    /**
     * 更新用户信息
     *
     * @param user     // 用户实体
     * @return void    // 无返回
     */
    void updateInfo(User user);

    /**
     * 新增用户
     *
     * @param user     // 用户实体
     * @return void    // 无返回
     */
    void addUser(User user);
}
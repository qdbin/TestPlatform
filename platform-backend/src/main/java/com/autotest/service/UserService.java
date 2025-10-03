package com.autotest.service;

import com.autotest.common.exception.PwdVerifyException;
import com.autotest.domain.*;
import com.autotest.dto.UserDTO;
import com.autotest.request.PasswordRequest;
import com.autotest.request.RegisterRequest;
import com.autotest.mapper.PermissionMapper;
import com.autotest.mapper.ProjectMapper;
import com.autotest.mapper.RoleMapper;
import com.autotest.mapper.UserMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;
/**
 * 服务：用户业务处理（查询、权限、注册）
 * 职责：维护用户基础信息、项目权限与注册流程
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class UserService {

    @Resource
    private UserMapper userMapper;

    @Resource
    private ProjectMapper projectMapper;

    @Resource
    private RoleMapper roleMapper;

    @Resource
    private PermissionMapper permissionMapper;

    /**
     * 获取用户基础信息
     *
     * @param id       // 用户ID
     * @return User    // 用户实体
     */
    public User getUserInfo(String id) {
        return userMapper.getUserInfo(id);
    }

    /**
     * 通过账号获取用户信息（含权限）
     *
     * @param account   // 登录账号
     * @return UserDTO  // 用户信息（扩展字段）
     */
    public UserDTO getUser(String account){
        return userMapper.getUser(account);
    }

    /**
     * 获取用户在项目下的权限码列表
     *
     * @param userId         // 用户ID
     * @param projectId      // 项目ID
     * @return List<String>  // 权限编码集合
     */
    public List<String> getUserProjectPermission(String userId, String projectId){
        return permissionMapper.getUserPermissionByProject(projectId, userId);
    }

    /**
     * 获取所有用户列表
     *
     * @return List<User>   // 用户列表
     */
    public List<User> getAllUser(){
        return userMapper.getAllUser();
    }

    /**
     * 模糊查询用户
     *
     * @param account     // 账号关键字
     * @return List<User> // 用户列表
     */
    public List<User> queryUser(String account){
        return userMapper.queryUser(account);
    }

    /**
     * 查询用户在项目下的角色ID列表
     *
     * @param projectId      // 项目ID
     * @param userId         // 用户ID
     * @return List<String>  // 角色ID集合
     */
    public List<String> getUserRoleList(String projectId, String userId){
        return userMapper.getUserRoleList(projectId, userId);
    }

    /**
     * 切换用户当前项目并刷新权限
     *
     * @param id           // 用户ID
     * @param projectId    // 目标项目ID
     * @return UserDTO     // 更新后的用户信息（含权限）
     *
     * 示例：切换到新项目后重新计算并赋值权限列表
     */
    public UserDTO switchProject(String id, String projectId) {
        userMapper.updateProject(id, projectId);
        UserDTO userDTO = userMapper.getUserInfo(id);
        userDTO.setPermissions(this.getUserProjectPermission(id, projectId));
        return userDTO;
    }

    /**
     * 更新用户密码（校验旧密码）
     *
     * @param request   // 密码请求载体（userId/old/new）
     * @return void     // 无返回
     *
     * 关键：旧密码不匹配抛出校验异常
     */
    public void updatePassword(PasswordRequest request) {
        User user = userMapper.getUserInfo(request.getUserId());
        if(!user.getPassword().equals(request.getOldPassword())){
            throw new PwdVerifyException("旧密码输入错误");
        }
        userMapper.updatePassword(request.getUserId(), request.getNewPassword());
    }

    /**
     * 更新用户资料（时间戳刷新）
     *
     * @param user    // 用户实体（更新字段）
     * @return void   // 无返回
     */
    public void updateInfo(User user) {
        user.setUpdateTime(System.currentTimeMillis());
        userMapper.updateInfo(user);
    }

    /**
     * 用户注册：创建用户并绑定默认项目与角色
     *
     * @param request // 注册信息：`username/account/password/mobile/email`
     * @return String // 结果提示字符串
     *
     * 数据示例：
     *   入参 = {username:"Tom", account:"tom", password:"123456", mobile:13800000000, email:"t@a.com"}
     *   调用 = this.registerUser(request)
     *   返回 = "注册成功" 或错误提示
     */
    public String registerUser(RegisterRequest request){
        // 校验：账号是否已注册
        User oldAccountUser = userMapper.getUser(request.getAccount()); // 通过账号查询
        if(oldAccountUser != null){
            return "该登录账号已被注册!"; // 命中直接返回提示
        }
        // 校验：手机号是否已注册
        User oldMobileUser = userMapper.getUser(request.getMobile().toString()); // 通过手机号查询
        if(oldMobileUser != null){
            return "该手机号已被注册!"; // 命中直接返回提示
        }
        // 查询：演示项目与默认角色
        Project project = projectMapper.getProjectByName("演示项目"); // 获取默认项目
        Role role = roleMapper.getRoleByProjectAndName(project.getId(), "项目普通用户"); // 获取默认角色
        // 构建并保存用户
        User user = new User(); // 新建用户实体
        user.setId(UUID.randomUUID().toString()); // 生成唯一ID
        user.setUsername(request.getUsername()); // 设置用户名
        user.setAccount(request.getAccount()); // 设置账号
        user.setMobile(request.getMobile()); // 设置手机号
        user.setEmail(request.getEmail()); // 设置邮箱
        user.setPassword(request.getPassword()); // 设置密码
        user.setCreateTime(System.currentTimeMillis()); // 设置创建时间
        user.setUpdateTime(System.currentTimeMillis()); // 设置更新时间
        user.setLastProject(project.getId()); // 默认项目
        userMapper.addUser(user); // 持久化用户
        // 建立用户与项目关联
        UserProject userProject = new UserProject(); // 创建关联实体
        userProject.setId(UUID.randomUUID().toString()); // 生成唯一ID
        userProject.setUserId(user.getId()); // 关联用户ID
        userProject.setProjectId(project.getId()); // 关联项目ID
        userProject.setCreateTime(System.currentTimeMillis()); // 创建时间
        userProject.setUpdateTime(System.currentTimeMillis()); // 更新时间
        projectMapper.addProjectUser(userProject); // 保存关联
        // 绑定用户角色
        UserRole userRole = new UserRole(); // 创建角色关联
        userRole.setId(UUID.randomUUID().toString()); // 生成唯一ID
        userRole.setUserId(user.getId()); // 关联用户ID
        userRole.setRoleId(role.getId()); // 关联角色ID
        userRole.setCreateTime(System.currentTimeMillis()); // 创建时间
        userRole.setUpdateTime(System.currentTimeMillis()); // 更新时间
        roleMapper.addRoleUser(userRole); // 保存关联
        return "注册成功"; // 返回结果提示
    }
}

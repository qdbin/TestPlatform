package com.autotest.controller;

import com.autotest.domain.User;
import com.autotest.dto.UserDTO;
import com.autotest.request.PasswordRequest;
import com.autotest.service.UserService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
    * 控制器：用户管理入口
    * 职责：用户信息、项目切换、密码与资料更新、角色与查询
    */
@RestController
@RequestMapping("/autotest/user")
public class UserController {

    @Resource
    private UserService userService;

    /**
        * 功能：查询用户信息
        *
        * @param id     // 用户ID
        * @return User  // 用户实体
        */
    @GetMapping("/info/{id}")
    public User getUserInfo(@PathVariable String id) {
        return userService.getUserInfo(id); // 直接透传至服务层
    }

    /**
        * 功能：切换所属项目
        *
        * @param user    // 用户实体（含lastProject）
        * @return UserDTO // 用户信息（含权限）
        */
    @PostMapping("/switch/project")
    public UserDTO switchProject(@RequestBody User user) {
        return userService.switchProject(user.getId(), user.getLastProject()); // 按传入项目ID切换
    }

    /**
        * 功能：更新用户密码
        *
        * @param request // 密码请求载体
        * @return void   // 无返回
        */
    @PostMapping("/update/password")
    public void updatePassword(@RequestBody PasswordRequest request) {
        userService.updatePassword(request); // 校验旧密码并更新
    }

    /**
        * 功能：更新用户资料
        *
        * @param user   // 用户实体
        * @return void // 无返回
        */
    @PostMapping("/update/info")
    public void updateInfo(@RequestBody User user) {
        userService.updateInfo(user); // 更新基础资料
    }

    /**
        * 功能：查询所有用户
        *
        * @return List<User> // 用户列表
        */
    @GetMapping("/all")
    public List<User> getAllUser(){
        return userService.getAllUser(); // 拉取全部用户
    }

    /**
        * 功能：查询用户在项目下的角色ID列表
        *
        * @param projectId  // 项目ID
        * @param userId     // 用户ID
        * @return List<String> // 角色ID列表
        */
    @GetMapping("/role/list")
    public List<String> getUserRoleList(@RequestParam String projectId, @RequestParam String userId) {
        return userService.getUserRoleList(projectId, userId); // 查询项目内角色
    }

    /**
        * 功能：模糊查询用户
        *
        * @param account   // 账号关键字
        * @return List<User> // 用户列表
        */
    @GetMapping("/query")
    public List<User> queryUser(@RequestParam String account) {
        return userService.queryUser(account); // 模糊匹配账号
    }
}
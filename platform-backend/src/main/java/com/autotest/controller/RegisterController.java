package com.autotest.controller;

import com.autotest.request.RegisterRequest;
import com.autotest.service.UserService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;


/**
 * 控制器：用户注册入口
 * 职责：接收注册请求并调用服务层完成注册流程。
 */
@RestController
@RequestMapping
public class RegisterController {

    @Resource
    private UserService userService;

    /**
     * 注册用户
     * @param request 注册请求（账号、密码、邮箱等）
     * @return String 注册结果（成功/失败信息）
     */
    @PostMapping("/autotest/register")
    public String registerUser(@RequestBody RegisterRequest request) {
        return userService.registerUser(request);
    }

}

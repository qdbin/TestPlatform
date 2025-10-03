package com.autotest.controller;

import com.autotest.common.exception.LoginVerifyException;
import com.autotest.common.utils.JwtUtils;
import com.autotest.dto.UserDTO;
import com.autotest.request.LoginRequest;
import com.autotest.service.UserService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletResponse;


/**
* 控制器：登录认证入口
* 用途：校验账号密码，生成并返回平台token
*/
@RestController
@RequestMapping
public class LoginController {

    @Resource
    private UserService userService;

    /**
    * 功能：登录并签发平台token
    * @param request    // 登录请求载体（account/password）
    * @param response   // 响应上下文（写入token）
    * @return UserDTO   // 用户信息（含权限，不含密码）
    *
    * 示例：
    *     入参：{"account":"user","password":"******"}
    *     调用：POST /autotest/login
    *     返回：header.token=JWT; body=用户信息
    */
    @PostMapping("/autotest/login")
    public UserDTO login(@RequestBody LoginRequest request, HttpServletResponse response) {
        UserDTO user = userService.getUser(request.getAccount());
        if(user != null) {
            // 关键：校验密码是否匹配
            if (user.getPassword().equals(request.getPassword())) {
                // 签发平台token并写入响应头
                response.addHeader("token", JwtUtils.createWebToken(user)); // 写入JWT到header
                user.setPassword(null); // 安全处理：清除密码字段
                // 刷新并设置权限列表
                user.setPermissions(userService.getUserProjectPermission(user.getId(), user.getLastProject())); // 计算权限
                return user; // 返回用户信息
            } else {
                // 密码校验失败
                throw new LoginVerifyException("账户密码校验失败");
            }
        }else{
            // 用户不存在
            throw new LoginVerifyException("用户不存在");
        }
}
}

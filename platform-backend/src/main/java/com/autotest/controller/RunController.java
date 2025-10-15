package com.autotest.controller;

import com.autotest.dto.TaskDTO;
import com.autotest.request.RunRequest;
import com.autotest.service.RunService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;


/**
 * 控制器：任务执行入口
 * 职责：接收前端执行请求，补齐运行用户信息并委派至服务层。
 */
@RestController
@RequestMapping("")
public class RunController {

    @Resource
    private RunService runService; // 任务执行服务

    /**
     * 发起执行任务
     * 功能：接收执行参数，补齐运行用户，委派服务层创建任务并通知引擎
     *
     * @param runRequest // 执行请求（来源、环境、引擎、设备等）
     * @param request    // Http 请求（用于获取 session 中的 userId）
     * @return TaskDTO   // 新建任务数据（含任务ID、报告ID等）
     */
    @PostMapping("/autotest/run")
    public TaskDTO run(@RequestBody RunRequest runRequest, HttpServletRequest request) {
        // 从 Session 获取运行用户
        String user = request.getSession().getAttribute("userId").toString(); // 获取 userId
        runRequest.setRunUser(user); // 写入运行用户
        return runService.run(runRequest); // 委派任务创建与通知
    }
}

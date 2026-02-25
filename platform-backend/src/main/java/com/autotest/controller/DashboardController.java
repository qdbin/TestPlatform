package com.autotest.controller;

import com.alibaba.fastjson.JSONObject;
import com.autotest.service.DashboardService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;


/**
 * 控制器：仪表盘数据入口
 * 职责：提供项目仪表盘数据聚合查询接口。
 */
@RestController
@RequestMapping("/autotest/dashboard")
public class DashboardController {

    @Resource
    private DashboardService dashboardService;

    /**
     * 查询项目仪表盘数据
     *
     * @param projectId // 项目ID
     * @return JSONObject // 仪表盘数据（含统计指标与图表数据）
     */
    @GetMapping("/get/{projectId}")
    public JSONObject getDashboardData(@PathVariable String projectId) {
        return dashboardService.getDashboardData(projectId);
    }

}

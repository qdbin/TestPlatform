package com.autotest.job;

import com.autotest.service.ScheduleJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * 定时任务：计划调度触发
 * 职责：按固定频率触发计划扫描与任务下发（高频：runSchedulePlan）
 * 示例：入口 updateTimeoutTask -> ScheduleJobService.runSchedulePlan()
 */
@Component
public class PlanScheduleJob {

    @Resource
    ScheduleJobService scheduleJobService;

    /**
     * 功能：按分钟触发计划扫描与下发
     * 
     * @return void // 无返回
     * 
     * 示例：定时 -> runSchedulePlan() -> 通知引擎拉取任务
     */
    @Scheduled(cron = "0 0/1 * * * ?") // 每分钟执行一次
    public void updateTimeoutTask(){
        // 触发计划扫描与任务创建
        scheduleJobService.runSchedulePlan();
    }
}

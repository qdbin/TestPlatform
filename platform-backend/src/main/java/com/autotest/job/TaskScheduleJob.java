package com.autotest.job;

import com.autotest.service.ScheduleJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * 定时任务：任务超时处理
 * 职责：周期性检测任务状态并执行超时更新
 * 示例：入口 updateTimeoutTask -> ScheduleJobService.updateTimeoutTask()
 */
@Component
public class TaskScheduleJob {

    @Resource
    ScheduleJobService scheduleJobService;

    /**
     * 功能：按三分钟检测并处理超时任务
     * 
     * @return void // 无返回
     * 
     * 示例：定时 -> updateTimeoutTask() -> 状态更新
     */
    @Scheduled(cron = "0 0/3 * * * ?") // 三分钟执行一次
    public void updateTimeoutTask(){
        // 执行任务超时检测与状态更新
        scheduleJobService.updateTimeoutTask();
    }
}

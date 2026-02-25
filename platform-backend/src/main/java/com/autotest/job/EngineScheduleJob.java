package com.autotest.job;

import com.autotest.service.ScheduleJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * 定时任务：引擎心跳监测
 * 职责：定时标记丢失心跳的引擎为异常状态
 * 示例：入口 updateLostHeartbeatEngine -> ScheduleJobService.updateLostHeartbeatEngine()
 */
@Component
public class EngineScheduleJob {

    @Resource
    ScheduleJobService scheduleJobService;

    /**
     * 功能：按分钟检测引擎心跳并更新异常状态
     * 
     * @return void // 无返回
     * 
     * 示例：定时 -> updateLostHeartbeatEngine() -> mapper.updateLostHeartbeatEngine
     */
    @Scheduled(cron = "0 0/1 * * * ?") // 每分钟执行一次
    public void updateLostHeartbeatEngine(){
        // 标记超过阈值未心跳的引擎
        scheduleJobService.updateLostHeartbeatEngine();
    }
}

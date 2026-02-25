package com.autotest.job;

import com.autotest.service.ScheduleJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * 定时任务：设备超时处理
 * 职责：周期性检查设备在线超时并执行冷却处理
 * 示例：入口 updateTimeoutDevice -> ScheduleJobService.updateTimeoutDevice()
 */
@Component
public class DeviceScheduleJob {

    @Resource
    ScheduleJobService scheduleJobService;

    /**
     * 功能：按分钟处理超时设备的冷却与状态
     * 
     * @return void // 无返回
     * 
     * 示例：定时 -> updateTimeoutDevice() -> deviceService.coldDevice
     */
    @Scheduled(cron = "0 0/1 * * * ?") // 一分钟执行一次
    public void updateTimeoutDevice(){
        // 检测设备超时并执行冷却流程
        scheduleJobService.updateTimeoutDevice();
    }
}

package com.autotest.job;

import com.autotest.service.ScheduleJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

/**
 * 定时任务：统计数据汇总
 * 职责：周期性聚合项目各类用例与计划的运行统计
 * 示例：入口 statisticsData -> ScheduleJobService.statisticsData()
 */
@Component
public class StatisticsScheduleJob {

    @Resource
    ScheduleJobService scheduleJobService;

    /**
     * 功能：按三分钟聚合与落库统计数据
     * 
     * @return void // 无返回
     * 
     * 示例：定时 -> statisticsData() -> 汇总今日与周度指标
     */
    @Scheduled(cron = "0 0/3 * * * ?") // 三分钟执行一次
    public void statisticsData(){
        // 触发统计数据汇总与更新
        scheduleJobService.statisticsData();
    }
}

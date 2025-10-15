package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.*;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.dto.StatisticsDTO;
import com.autotest.websocket.config.WsSessionManager;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import javax.annotation.Resource;
import java.text.SimpleDateFormat;
import java.util.*;


/**
 * 服务：定时任务业务处理
 * 职责：引擎心跳、任务/设备超时、计划调度、统计汇总
 * 示例：runSchedulePlan -> 任务/报告预设 -> 通知引擎拉取任务
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ScheduleJobService {

    @Resource
    private EngineMapper engineMapper; // 引擎数据访问

    @Resource
    private TaskMapper taskMapper; // 任务数据访问

    @Resource
    private ReportMapper reportMapper; // 报告数据访问

    @Resource
    private PlanMapper planMapper; // 计划数据访问

    @Resource
    private PlanScheduleMapper planScheduleMapper; // 计划调度数据访问

    @Resource
    private PlanCollectionMapper planCollectionMapper; // 计划集合数据访问

    @Resource
    private StatisticsMapper statisticsMapper; // 统计数据访问

    @Resource
    private ProjectMapper projectMapper; // 项目数据访问

    @Resource
    private DeviceMapper deviceMapper; // 设备数据访问

    @Resource
    private RunService runService; // 运行服务

    @Resource
    private DeviceService deviceService; // 设备服务

    /**
     * 功能：标记丢失心跳的引擎为离线
     * 
     * @return void // 无返回
     * 
     * 示例：当前时间-3分钟 -> mapper.updateLostHeartbeatEngine(minLastHeartbeatTime)
     */
    public void updateLostHeartbeatEngine(){
        Long minLastHeartbeatTime = System.currentTimeMillis() - 3*60*1000; // 三分钟没有心跳监控则离线
        engineMapper.updateLostHeartbeatEngine(minLastHeartbeatTime);
    }

    /**
     * 功能：处理任务超时（长时间未上传结果或未执行）
     * 
     * @return void // 无返回
     * 
     * 示例：selectTimeoutReport -> 更新任务/报告状态 -> 释放设备/通知引擎停止
     */
    public void updateTimeoutTask(){
        Long minLastUploadTime = System.currentTimeMillis() - 10*60*1000;   // 十分钟内没有结果返回则任务超时
        Long minLastToRunTime = System.currentTimeMillis() - 2*60*60*1000;   // 两小时内没有执行则任务超时
        List<Report> reports = reportMapper.selectTimeoutReport(minLastUploadTime, minLastToRunTime);
        // 遍历超时报告并处理任务/设备
        for(Report report:reports){
            reportMapper.updateReportStatus(ReportStatus.DISCONTINUE.toString(), report.getId());
            taskMapper.updateTask(ReportStatus.DISCONTINUE.toString(), report.getTaskId());
            reportMapper.updateReportEndTime(report.getId(), System.currentTimeMillis(), System.currentTimeMillis());
            // 释放设备
            runService.stopDeviceWhenRunEnd(report.getTaskId());
            Task task  = taskMapper.getTaskDetail(report.getTaskId());
            if(!task.getEngineId().equals(EngineType.SYSTEM.toString())){
                try {
                    WebSocketSession session = WsSessionManager.get("engine", task.getEngineId());
                    JSONObject message = new JSONObject();
                    message.put("type", "stop");
                    message.put("data", task.getId());
                    session.sendMessage(new TextMessage(message.toString()));
                }catch (Exception ignored){
                }
            }
        }
    }

    /**
     * 功能：处理设备在线超时并执行冷却
     * 
     * @return void // 无返回
     * 
     * 示例：selectTimeoutDevice -> deviceService.coldDevice(device)
     */
    public void updateTimeoutDevice(){
        List<Device> devices = deviceMapper.selectTimeoutDevice();
        // 遍历超时设备并执行冷却
        for (Device device:devices){
            deviceService.coldDevice(device);
        }
    }

    /**
     * 功能：执行计划调度，创建任务/报告并通知引擎拉取
     * 
     * @return void // 无返回
     * 
     * 示例：getToRunPlanScheduleList -> 预设任务/报告 -> 通知引擎 start
     */
    public void runSchedulePlan(){
        long currentTime = System.currentTimeMillis();
        Long minNextRunTime = currentTime - 30*1000;
        Long maxNextRunTime = currentTime + 30*1000;   // 查找下次执行时间在前后半分钟内的计划
        List<PlanSchedule> planSchedules = planScheduleMapper.getToRunPlanScheduleList(minNextRunTime, maxNextRunTime);

        // 遍历待运行计划，创建任务与报告并通知引擎
        for(PlanSchedule planSchedule: planSchedules){
            Plan plan = planMapper.getPlanDetail(planSchedule.getPlanId());
            String runName = "【定时执行】" + plan.getName() +"-"+ new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date(planSchedule.getNextRunTime()));
            Task task = new Task();
            task.setId(UUID.randomUUID().toString());
            task.setName(runName);
            task.setStatus(ReportStatus.PREPARED.toString());
            task.setType(TaskType.SCHEDULE.toString());
            task.setEngineId(plan.getEngineId());
            task.setProjectId(plan.getProjectId());
            task.setCreateUser(plan.getCreateUser());
            task.setUpdateUser(plan.getCreateUser());
            task.setCreateTime(System.currentTimeMillis());
            task.setUpdateTime(System.currentTimeMillis());
            taskMapper.addTask(task);

            // 预设报告
            Report report = new Report();
            report.setId(UUID.randomUUID().toString());
            report.setName(runName);
            report.setTaskId(task.getId());
            report.setEnvironmentId(plan.getEnvironmentId());
            report.setDeviceId(null);
            report.setSourceType(ReportSourceType.PLAN.toString());
            report.setSourceId(plan.getId());
            report.setStatus(ReportStatus.PREPARED.toString());
            report.setProjectId(plan.getProjectId());
            report.setCreateUser(plan.getCreateUser());
            report.setUpdateUser(plan.getCreateUser());
            report.setCreateTime(System.currentTimeMillis());
            report.setUpdateTime(System.currentTimeMillis());
            reportMapper.addReport(report);

            // 统计报告用例数
            ReportStatistics reportStatistics = new ReportStatistics();
            reportStatistics.setId(UUID.randomUUID().toString());
            reportStatistics.setReportId(report.getId());
            reportStatistics.setPassCount(0);
            reportStatistics.setErrorCount(0);
            reportStatistics.setFailCount(0);
            Integer total = planCollectionMapper.getPlanCaseCount(plan.getId());
            reportStatistics.setTotal(total);
            reportMapper.addReportStatistics(reportStatistics);

            // 回写定时任务表下次执行时间
            while (!planSchedule.getFrequency().equals(PlanFrequency.ONLY_ONE.toString()) && planSchedule.getNextRunTime() < maxNextRunTime){ // 找到大于当前时间的日期
                planSchedule.setNextRunTime(PlanService.getNextRunTime(planSchedule.getNextRunTime(), planSchedule.getFrequency()));
            }
            planScheduleMapper.updatePlanSchedule(planSchedule);

            // 通知系统引擎或指定引擎拉取任务
            if(plan.getEngineId().equals(EngineType.SYSTEM.toString())){
                List<Engine> engineList = engineMapper.getAllSystemEngine();
                for(Engine engine: engineList){ // 通知所有在线的引擎来获取任务
                    try {
                        WebSocketSession session = WsSessionManager.get("engine", engine.getId()); // 获取会话
                        JSONObject message = new JSONObject();
                        message.put("type", "start"); // 指令：开始
                        session.sendMessage(new TextMessage(message.toString())); // 发送开始指令
                    }catch (Exception ignored){
                    }
                }
            }else {
                try {
                    WebSocketSession session = WsSessionManager.get("engine", plan.getEngineId()); // 获取会话
                    JSONObject message = new JSONObject();
                    message.put("type", "start"); // 指令：开始
                    session.sendMessage(new TextMessage(message.toString())); // 发送指令
                }catch (Exception ignored){
                }
            }
        }
    }

    /**
     * 功能：统计项目维度的每日/周度运行与用例指标并落库
     * 
     * @return void // 无返回
     * 
     * 示例：聚合统计DTO -> 更新 SumStatistics/DailyStatistics 表
     */
    public void statisticsData(){
        // 所有项目
        List<String> projectIds = projectMapper.getAllProjectId();
        // 当前日期
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        String currentDate = sdf.format(date);
        // 总数统计
        HashMap<String, SumStatistics> sumStatisticsMap = new HashMap<>();
        // 每日统计
        HashMap<String, DailyStatistics> dailyStatisticsMap = new HashMap<>();

        for(String projectId: projectIds){
            SumStatistics sum = new SumStatistics();
            sum.setId(UUID.randomUUID().toString());
            sum.setProjectId(projectId);
            JSONObject prObj = new JSONObject();
            prObj.put("xAxis", new JSONArray());
            prObj.put("planRunTotal", new JSONArray());
            prObj.put("planRunPass", new JSONArray());
            prObj.put("planRunPassRate", new JSONArray());
            prObj.put("yMaxLeft", 0);
            sum.setPlanRunWeekTop(prObj.toString());
            JSONObject cfObj = new JSONObject();
            cfObj.put("x", new JSONArray());
            cfObj.put("y", new JSONArray());
            sum.setCaseFailWeekTop(cfObj.toString());
            sumStatisticsMap.put(projectId, sum);
            DailyStatistics daily = new DailyStatistics();
            daily.setId(UUID.randomUUID().toString());
            daily.setProjectId(projectId);
            daily.setStatDate(currentDate);
            dailyStatisticsMap.put(projectId, daily);
        }

        List<StatisticsDTO> caseTotal = statisticsMapper.getCaseCountByProject();
        for(StatisticsDTO statisticsDTO: caseTotal){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            DailyStatistics daily = dailyStatisticsMap.get(statisticsDTO.getProjectId());
            if(statisticsDTO.getName().equals("API")){
                sum.setApiCaseTotal(statisticsDTO.getCount());
                daily.setApiCaseSum(statisticsDTO.getCount());
            }else if(statisticsDTO.getName().equals("WEB")){
                sum.setWebCaseTotal(statisticsDTO.getCount());
                daily.setWebCaseSum(statisticsDTO.getCount());
            }else {
                sum.setAppCaseTotal(statisticsDTO.getCount());
                daily.setAppCaseSum(statisticsDTO.getCount());
            }
        }
        List<StatisticsDTO> caseNewToday = statisticsMapper.getCaseTodayNewCountByProject();
        for(StatisticsDTO statisticsDTO: caseNewToday){
            DailyStatistics daily = dailyStatisticsMap.get(statisticsDTO.getProjectId());
            if(statisticsDTO.getName().equals("API")){
                daily.setApiCaseNew(statisticsDTO.getCount());
            }else if(statisticsDTO.getName().equals("WEB")){
                daily.setWebCaseNew(statisticsDTO.getCount());
            }else {
                daily.setAppCaseNew(statisticsDTO.getCount());
            }
        }
        List<StatisticsDTO> caseNewWeek = statisticsMapper.getCaseWeekNewCountByProject();
        for (StatisticsDTO statisticsDTO: caseNewWeek){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            if (statisticsDTO.getName().equals("API")){
                sum.setApiCaseNewWeek(statisticsDTO.getCount());
            }else if(statisticsDTO.getName().equals("WEB")){
                sum.setWebCaseNewWeek(statisticsDTO.getCount());
            }else {
                sum.setAppCaseNewWeek(statisticsDTO.getCount());
            }
        }
        List<StatisticsDTO> caseRunToday = statisticsMapper.getCaseTodayRunCountByProject();
        for (StatisticsDTO statisticsDTO: caseRunToday){
            DailyStatistics daily = dailyStatisticsMap.get(statisticsDTO.getProjectId());
            if (statisticsDTO.getName().equals("API")){
                daily.setApiCaseRun(statisticsDTO.getCount());
                daily.setApiCasePassRate(statisticsDTO.getPassRate());
            }else if(statisticsDTO.getName().equals("WEB")){
                daily.setWebCaseRun(statisticsDTO.getCount());
                daily.setWebCasePassRate(statisticsDTO.getPassRate());
            }else {
                daily.setAppCaseRun(statisticsDTO.getCount());
                daily.setAppCasePassRate(statisticsDTO.getPassRate());
            }
        }
        List<StatisticsDTO> caseRunTotal = statisticsMapper.getCaseTotalRunCountByProject();
        for (StatisticsDTO statisticsDTO: caseRunTotal){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            sum.setCaseRunTotal(statisticsDTO.getCount());
        }
        List<StatisticsDTO> caseRunTotalToday = statisticsMapper.getCaseTotalTodayRunCountByProject();
        for (StatisticsDTO statisticsDTO: caseRunTotalToday){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            sum.setCaseRunToday(statisticsDTO.getCount());
        }
        List<StatisticsDTO> planRunTop = statisticsMapper.getPlanRunTopByProject();
        for (StatisticsDTO statisticsDTO: planRunTop){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            JSONObject planRunObj = JSONObject.parseObject(sum.getPlanRunWeekTop());
            planRunObj.getJSONArray("xAxis").add(statisticsDTO.getName());
            planRunObj.getJSONArray("planRunTotal").add(statisticsDTO.getCount());
            planRunObj.getJSONArray("planRunPass").add(statisticsDTO.getPass());
            planRunObj.getJSONArray("planRunPassRate").add(statisticsDTO.getPassRate());
            if (planRunObj.getInteger("yMaxLeft") < statisticsDTO.getCount()){
                planRunObj.put("yMaxLeft", statisticsDTO.getCount());
            }
            sum.setPlanRunWeekTop(planRunObj.toString());
        }
        List<StatisticsDTO> caseFailTop = statisticsMapper.getCaseFailTopByProject();
        for (StatisticsDTO statisticsDTO: caseFailTop){
            SumStatistics sum = sumStatisticsMap.get(statisticsDTO.getProjectId());
            JSONObject caseFailObj = JSONObject.parseObject(sum.getCaseFailWeekTop());
            caseFailObj.getJSONArray("x").add(statisticsDTO.getCount());
            caseFailObj.getJSONArray("y").add(statisticsDTO.getName());
            sum.setCaseFailWeekTop(caseFailObj.toString());
        }
        List<SumStatistics> sumStatisticsList = new ArrayList<>(sumStatisticsMap.values());
        statisticsMapper.updateSumData(sumStatisticsList);
        List<DailyStatistics> dailyStatisticsList = new ArrayList<>(dailyStatisticsMap.values());
        statisticsMapper.updateDailyData(dailyStatisticsList);
    }
}

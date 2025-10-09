package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.DeviceStatus;
import com.autotest.common.constants.EngineType;
import com.autotest.common.constants.ReportSourceType;
import com.autotest.common.constants.ReportStatus;
import com.autotest.common.exception.LMException;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.dto.PlanCollectionDTO;
import com.autotest.dto.TaskDTO;
import com.autotest.request.RunRequest;
import com.autotest.websocket.config.WsSessionManager;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import javax.annotation.Resource;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.UUID;

/**
 * 服务：执行任务触发与设备占用管理
 * 职责：
 * - 发起任务与预置报告；
 * - 调试数据落库（TEMP 源）；
 * - 系统/指定引擎通知拉取任务；
 * - 用例执行结束后释放占用设备。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class RunService {
    @Resource
    private TaskMapper taskMapper; // 任务数据访问

    @Resource
    private ReportMapper reportMapper; // 报告数据访问

    @Resource
    private PlanCollectionMapper planCollectionMapper; // 计划-集合映射访问

    @Resource
    private CollectionCaseMapper collectionCaseMapper; // 集合-用例映射访问

    @Resource
    private DebugDataMapper debugDataMapper; // 调试数据访问

    @Resource
    private DeviceMapper deviceMapper; // 设备数据访问

    @Resource
    private EngineMapper engineMapper; // 引擎数据访问

    @Resource
    private CollectionMapper collectionMapper; // 集合数据访问

    @Resource
    private DeviceService deviceService; // 设备操作服务

    /**
     * 发起执行任务（写入任务与预设报告，并通知引擎）
     * @param runRequest 运行请求（包含来源、引擎、环境、设备等）
     * @return TaskDTO   新建任务信息（含任务ID、报告ID等）
     */
    public TaskDTO run(RunRequest runRequest) {
        // 新增任务（初始化任务基本信息）
        TaskDTO task = new TaskDTO();
        task.setId(UUID.randomUUID().toString()); // 随机任务ID

        // 执行引擎为 App 设备时占用设备并校验状态
        if(runRequest.getDeviceId() != null && !runRequest.getDeviceId().equals("")){
            Device device = deviceMapper.getDeviceById(runRequest.getDeviceId());
            if((!device.getStatus().equals(DeviceStatus.ONLINE.toString())) &&
                    (!(device.getStatus().equals(DeviceStatus.USING.toString()) &&
                            runRequest.getRunUser().equals(device.getUser())))){
                // 设备需空闲；若设备使用中，使用者须为当前用户
                throw new LMException("设备非空闲状态 执行失败");
            }
            if(device.getStatus().equals(DeviceStatus.ONLINE.toString())) {
                // 空闲设备占用并置为测试中
                device.setStatus(DeviceStatus.TESTING.toString());
                device.setUpdateTime(System.currentTimeMillis());
                device.setUser(task.getId());   // 设备使用者绑定任务ID
                device.setTimeout(-1);  // 测试中设备不超时
                deviceMapper.updateDevice(device);  // 占用设备
            }
        }

        // 调试（源类型:temp）:入库DebugData,并更新sourceId字段
        if(runRequest.getSourceType().equals(ReportSourceType.TEMP.toString())){
            DebugData debugData = new DebugData();
            debugData.setId(UUID.randomUUID().toString());                          // 临时数据ID
            debugData.setData(JSONObject.toJSONString(runRequest.getDebugData()));  // 调试数据内容
            debugDataMapper.addDebugData(debugData);                                // 写入临时表
            runRequest.setSourceId(debugData.getId());                              // 更新源id(由原case_id改为DebugData_id)
        }

        // 新增task(填充task相关信息)
        String runName = runRequest.getSourceName() +"-"+ new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()); // 任务名称含时间戳
        task.setName(runName);
        task.setStatus(ReportStatus.PREPARED.toString());   // Prepared（状态）
        task.setType(runRequest.getTaskType());             // debug/run（类型）
        task.setEngineId(runRequest.getEngineId());         // enginId
        task.setProjectId(runRequest.getProjectId());       // projectId
        task.setCreateUser(runRequest.getRunUser());
        task.setUpdateUser(runRequest.getRunUser());
        task.setCreateTime(System.currentTimeMillis());
        task.setUpdateTime(System.currentTimeMillis());
        taskMapper.addTask(task);                           // 写入任务

        // 新增报告（与任务绑定）
        Report report = new Report();
        report.setId(UUID.randomUUID().toString());
        report.setName(runName);
        report.setTaskId(task.getId());                             // taskId
        report.setEnvironmentId(runRequest.getEnvironmentId());     // environmentId
        report.setDeviceId(runRequest.getDeviceId());
        report.setSourceType(runRequest.getSourceType());           // 报告类型（tmp/case/collection/plan）
        report.setSourceId(runRequest.getSourceId());               // sourceId
        report.setStatus(ReportStatus.PREPARED.toString());         // prepared（状态:prepared/skip/discontinue/error/success）
        report.setProjectId(runRequest.getProjectId());             // projectId
        report.setCreateUser(runRequest.getRunUser());
        report.setUpdateUser(runRequest.getRunUser());
        report.setCreateTime(System.currentTimeMillis());
        report.setUpdateTime(System.currentTimeMillis());
        reportMapper.addReport(report);                             // 写入报告

        // 新增报告统计（与报告绑定）（用例总数（通过、失败、错误））
        ReportStatistics reportStatistics = new ReportStatistics();
        reportStatistics.setId(UUID.randomUUID().toString());
        reportStatistics.setReportId(report.getId());               // reportId
        reportStatistics.setPassCount(0);
        reportStatistics.setErrorCount(0);
        reportStatistics.setFailCount(0);
        // 确定不同任务的用例总数（plan、collection、case/temp）
        Integer total = 0;
        if(runRequest.getSourceType().equals(ReportSourceType.PLAN.toString())){
            total = planCollectionMapper.getPlanCaseCount(runRequest.getSourceId());    // plan用例数
        }else if(runRequest.getSourceType().equals(ReportSourceType.COLLECTION.toString())){
            total = collectionCaseMapper.getCollectionCaseCount(runRequest.getSourceId());  // collection用例数
        }else {
            total = 1;  // case/temp用例数（恒为1）
        }
        reportStatistics.setTotal(total);
        reportMapper.addReportStatistics(reportStatistics); // 写入统计

        // task绑定reportId
        task.setReportId(report.getId());

        // 系统引擎(广播通知所有在线系统引擎拉取任务)
        if(runRequest.getEngineId().equals(EngineType.SYSTEM.toString())){
            List<Engine> engineList = engineMapper.getAllSystemEngine();
            for(Engine engine: engineList){ // 遍历在线引擎并通知
                try {
                    WebSocketSession session = WsSessionManager.get("engine", engine.getId()); // 获取会话
                    JSONObject message = new JSONObject();
                    message.put("type", "start"); // 指令：开始拉取任务
                    session.sendMessage(new TextMessage(message.toString())); // 发送通知
                }catch (Exception ignored){
                }
            }
        }
        
        // 自定义引擎(通知指定引擎拉取任务)
        else {
            try {
                WebSocketSession session = WsSessionManager.get("engine", runRequest.getEngineId()); // 获取会话
                JSONObject message = new JSONObject();
                message.put("type", "start"); // 指令：开始拉取任务
                session.sendMessage(new TextMessage(message.toString())); // 发送通知
            }catch (Exception ignored){
            }
        }
        return task; // 返回新建任务
    }

    /**
     * 任务执行结束释放设备（仅在占用者为本任务时）
     * @param taskId 任务ID
     */
    public void stopDeviceWhenRunEnd(String taskId){
        TaskDTO task = taskMapper.getTaskDetail(taskId); // 查询任务
        if(task.getDeviceId() != null) {
            Device device = deviceService.getDeviceDetail(task.getDeviceId()); // 获取设备详情
            if(device.getStatus().equals(DeviceStatus.TESTING.toString()) &&
                    task.getId().equals(device.getUser())){
                deviceService.coldDevice(device); // 当前设备使用者仍为任务则停用
            }
        }else if(task.getSourceType().equals(ReportSourceType.PLAN.toString())){
            List<PlanCollectionDTO> planCollections = planCollectionMapper.getPlanCollectionList(task.getSourceId()); // 获取计划集合列表
            for(PlanCollectionDTO planCollectionDTO:planCollections){
                Collection collection = collectionMapper.getCollectionDetail(planCollectionDTO.getCollectionId()); // 查询集合
                if(collection==null) return;
                if(collection.getDeviceId() != null){
                    Device device = deviceService.getDeviceDetail(collection.getDeviceId()); // 获取设备详情
                    if(device.getStatus().equals(DeviceStatus.TESTING.toString()) &&
                            task.getId().equals(device.getUser())){
                        deviceService.coldDevice(device); // 当前设备使用者仍为任务则停用
                    }
                }
            }
        }
    }

}

package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.*;
import com.autotest.common.exception.EngineVerifyException;
import com.autotest.common.exception.LMException;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.common.utils.FileUtils;
import com.autotest.common.utils.ImageUtils;
import com.autotest.common.utils.JwtUtils;
import com.autotest.common.utils.UploadUtils;
import com.autotest.dto.ReportDTO;
import com.autotest.dto.TaskDTO;
import com.autotest.request.CaseResultRequest;
import com.autotest.request.EngineRequest;
import com.autotest.request.RunRequest;
import com.autotest.response.TaskResponse;
import com.autotest.response.TaskTestCollectionResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletResponse;
import java.util.List;

/**
 * 服务：开放接口对接与执行驱动
 * 职责：对接外部引擎与任务执行，包括令牌申请、心跳、任务分发、结果回传、报告统计、文件与截图处理，以及计划外部触发与报告查询。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class OpenApiService {

    @Value("${task.file.path}")
    public String TASK_FILE_PATH;

    @Value("${app.package.path}")
    private String APP_PACKAGE_PATH; // 应用安装包根路径

    @Value("${mail.sender.on-off}")
    private String MAIL_ON_OFF; // 邮件通知开关（on/off）

    @Value("${spring.mail.username}")
    private String MAIL_SENDER; // 邮件发送账号
    
    @Value("${cloud.storage.on-off}")
    private String cloudStorage;  // 云存储开关（on/off）

    @Value("${report.screenshot.path}")
    private String imagePath;  // 截图本地存储路径

    @Value("${qiniu.cloud.ak}")
    private String ak;   // 七牛云 AK

    @Value("${qiniu.cloud.sk}")
    private String sk;    // 七牛云 SK

    @Value("${qiniu.cloud.bucket}")
    private String imageBucket;    // 七牛云空间名（存储图片）

    @Value("${qiniu.cloud.uploadUrl}")
    private String uploadUrl;   // 七牛云上传域名

    @Resource
    private UserMapper userMapper; // 用户数据访问

    @Resource
    private EngineMapper engineMapper; // 引擎数据访问

    @Resource
    private TaskMapper taskMapper; // 任务数据访问

    @Resource
    private ReportMapper reportMapper; // 报告数据访问

    @Resource
    private PlanMapper planMapper; // 测试计划数据访问

    @Resource
    private PlanNoticeMapper planNoticeMapper; // 计划通知配置访问

    @Resource
    private TestFileMapper testFileMapper; // 测试文件数据访问

    @Resource
    private DebugDataMapper debugDataMapper; // 调试数据访问

    @Resource
    private CaseJsonCreateService caseJsonCreateService; // 测试数据构建服务

    @Resource
    private ReportUpdateService reportUpdateService; // 报告更新服务

    @Resource
    private NotificationService notificationService; // 通知服务

    @Resource
    private RunService runService; // 运行与设备占用服务

    @Resource
    private ReportService reportService; // 报告查询服务

    @Resource
    private SendMailService sendMailService; // 邮件发送服务

    /**
     * 申请引擎令牌（校验引擎ID与秘钥）
     *
     * @param request // 引擎请求（engineCode/engineSecret）
     * @return String // 引擎JWT令牌
     */
    public String applyEngineToken(EngineRequest request) {
        Engine engine = engineMapper.getEngineById(request.getEngineCode());
        if (request.getEngineSecret().equals(engine.getSecret())){
            return JwtUtils.createEngineToken(engine);
        }
        throw new EngineVerifyException("id或secret填写不正确");
    }

    /**
     * 引擎心跳上报（在线/运行状态维护）
     *
     * @param request // 引擎请求（engineCode）
     * @return String // 心跳成功提示
     */
    public String engineHeartbeat(EngineRequest request) {
        Engine engine = engineMapper.getEngineById(request.getEngineCode());
        if(engine == null){
            throw new EngineVerifyException("引擎code不存在");
        }
        if (engine.getStatus().equals(EngineStatus.OFFLINE.toString())){
            engineMapper.updateStatus(request.getEngineCode(), EngineStatus.ONLINE.toString());
        }
        engineMapper.updateHeartbeat(request.getEngineCode(), System.currentTimeMillis());
        return "心跳成功";
    }

    /**
     * 引擎拉取待执行任务（含测试数据打包/调试数据生成）
     *
     * @param request // 引擎请求（engineCode）
     * @return TaskResponse // 任务响应（包含下载地址或调试数据）
     */
    public TaskResponse fetchEngineTask(EngineRequest request) {
        // Task响应
        TaskResponse response = new TaskResponse();

        // 获取引擎信息并校验
        Engine engine = engineMapper.getEngineById(request.getEngineCode());
        if(engine == null){
            throw new EngineVerifyException("引擎code不存在");
        }

        // 获取TaskDTo(根据engineCode获得status==prepared的任务)
        TaskDTO task; // 即将分配的任务
        if(engine.getEngineType().equals(EngineType.SYSTEM.toString())){
            // 内置引擎优先调试，其次计划/集合
            task = taskMapper.getToRunTask(EngineType.SYSTEM.toString());
        }else {
            task = taskMapper.getToRunTask(engine.getId());
        }

        // 异常情况处理
        if(task == null){
            return null;
        }
        if(engine.getEngineType().equals(EngineType.SYSTEM.toString())) {
            // 更新任务绑定引擎为当前引擎
            int count = taskMapper.updateTaskEngine(request.getEngineCode(), task.getId());
            if (count == 0){    // 该条任务被别的引擎拿到 不再返回 等待下一次请求
                return null;
            }
        }
        if(task.getSourceId() == null){ // sourceId为空就不能查找任务的具体内容
            return null;
        }

        // 组装collection_list（用于调试或下载数据）
        List<TaskTestCollectionResponse> testCollectionList = caseJsonCreateService.getTaskTestCollectionList(task);
        if(testCollectionList.size()==0) return null; // 无可执行用例

        // 设置debugData/url数据（tmp/case：debugData | collection/plan : url(json.zip)）
        try {
            // temp || case
            if (task.getSourceType().equals(ReportSourceType.TEMP.toString()) || task.getSourceType().equals(ReportSourceType.CASE.toString())) {
                // 获得DebugData(传入collection_list,根据case获得)
                JSONObject testCase = caseJsonCreateService.getDebugData(task, testCollectionList);
                response.setDownloadUrl(null);
                response.setDebugData(testCase);
            }
            // collection || plan
            else {
                // 计划/集合：生成数据包并返回下载地址
                String downloadUrl = caseJsonCreateService.getDownloadUrl(task, testCollectionList);
                response.setDebugData(null);
                response.setDownloadUrl(downloadUrl);
            }
        }catch (Exception e){   // 出现错误直接返回空数据
            response.setDownloadUrl(null);
            response.setDebugData(null);
        }

        // 设置reRun/maxThread（默认不重试和单线程）
        response.setReRun(false);
        response.setMaxThread(1);
        if(task.getSourceType().equals(ReportSourceType.PLAN.toString())){  // 根据计划的配置,更新重试和多线程
            Plan plan = planMapper.getPlanDetail(task.getSourceId());
            if(plan.getRetry().equals("Y")){
                response.setReRun(true); // 计划开启失败重试
            }
            response.setMaxThread(plan.getMaxThread()); // 按计划配置线程数
        }
        response.setTaskId(task.getId()); // 任务ID
        response.setTaskType(task.getType()); // 任务类型
        response.setTestCollectionList(testCollectionList); // 用例集合

        // 更新status（engin/task/report）
        engineMapper.updateStatus(engine.getId(), EngineStatus.RUNNING.toString());             // 引擎置为运行
        taskMapper.updateTask(ReportStatus.RUNNING.toString(), task.getId());                   // 任务置为运行
        reportMapper.updateReportStatus(ReportStatus.RUNNING.toString(), task.getReportId());   // 报告置为运行
        reportMapper.updateReportStartTime(task.getReportId(), System.currentTimeMillis(), System.currentTimeMillis()); // 记录开始时间

        return response;
    }

    /**
     * 查询任务状态（终止时释放设备并返回停止标记）
     *
     * @param request // 引擎请求（taskId）
     * @return String // "STOP" 表示任务被终止；否则返回null
     */
    public String getTaskStatus(EngineRequest request){
        TaskDTO task = taskMapper.getTaskDetail(request.getTaskId()); // 查询任务详情
        // 若任务被标记中断，释放设备并提示引擎停止
        if(task.getStatus().equals(ReportStatus.DISCONTINUE.toString())){
            engineMapper.updateStatus(task.getEngineId(), EngineStatus.ONLINE.toString()); // 引擎回置在线
            runService.stopDeviceWhenRunEnd(task.getId()); // 释放设备（占用者为本任务时）
            return "STOP"; // 返回停止标记
        }
        return null;
    }

    /**
     * 上传用例执行结果（写入报告统计）
     *
     * @param request // 引擎请求（taskId、caseResultList）
     * @return void   // 无返回
     */
    public void uploadCaseResult(EngineRequest request){
        TaskDTO task = taskMapper.getTaskDetail(request.getTaskId());           // 获取task_dto
        List<CaseResultRequest> caseResultList = request.getCaseResultList();   // 获取用例结果集
        reportUpdateService.updateReport(task, caseResultList);                 // 累计统计并更新报告
    }

    /**
     * 任务执行完成回调（更新报告状态、释放设备、通知）
     *
     * @param request // 引擎请求（taskId、engineCode）
     * @return void   // 无返回
     */
    public void completeEngineTask(EngineRequest request){
        TaskDTO task = taskMapper.getTaskDetail(request.getTaskId()); // 查询任务

        // 标记任务完成
        taskMapper.updateTask(ReportStatus.COMPLETED.toString(), task.getId());

        // 汇总报告统计以决策最终状态
        ReportStatistics reportStatistics = reportMapper.getReportStatistics(task.getReportId());

        // 最终报告状态
        String reportStatus;
        if(reportStatistics.getErrorCount() > 0){
            reportStatus = ReportStatus.ERROR.toString();
        }else if(reportStatistics.getFailCount() > 0){
            reportStatus = ReportStatus.FAIL.toString();
        }else if(reportStatistics.getPassCount() > 0){
            reportStatus = ReportStatus.SUCCESS.toString();
        }else {
            reportStatus = ReportStatus.SKIP.toString();
        }

        // 更新状态
        engineMapper.updateStatus(request.getEngineCode(), EngineStatus.ONLINE.toString()); // 引擎置为在线
        reportMapper.updateReportStatus(reportStatus, task.getReportId()); // 更新报告状态
        reportMapper.updateReportEndTime(task.getReportId(), System.currentTimeMillis(), System.currentTimeMillis()); // 记录结束时间

        // 释放设备
        runService.stopDeviceWhenRunEnd(task.getId()); // 占用者为本任务时冷却设备

        // 删除任务文件 并通知执行人
        if(!task.getType().equals(TaskType.DEBUG.toString())){
            String taskZipPath = TASK_FILE_PATH+"/"+task.getProjectId()+"/"+task.getId()+".zip"; // 任务数据包路径
            FileUtils.deleteFile(taskZipPath); // 清理任务数据包

            // 计划通知
            if(task.getSourceType().equals(ReportSourceType.PLAN.toString())){

                // 邮箱通知
                try {
                    if("on".equals(MAIL_ON_OFF)) {
                        // 邮件推送
                        User user = userMapper.getUserInfo(task.getCreateUser());
                        String title = "测试任务执行完成通知";
                        String content = user.getUsername() + ", 您好!<br><br>您执行的任务: \""
                                + task.getName() + "\" 已执行完毕，请登录平台查看结果。<br><br>谢谢！";
                        sendMailService.sendReportMail(MAIL_SENDER, user.getEmail(), title, content);
                    }
                }catch (Exception ignored){
                }

                // 群消息通知
                PlanNotice planNotice = planNoticeMapper.getPlanNotice(task.getSourceId());
                if(planNotice == null){
                    return; //没有配置不通知
                }
                if(planNotice.getCondition().equals("F") && reportStatus.equals(ReportStatus.SUCCESS.toString())){
                    return; // 仅失败通知且结果成功不通知
                }
                Notification notification = notificationService.getNotificationById(planNotice.getNotificationId());
                if(notification.getStatus().equals(NotificationStatus.DISABLE.toString())){
                    return; // 通知禁用不通知
                }
                try {
                    notificationService.sendNotification(notification, task);   // 发送通知
                }catch (Exception ignored){
                }
            }
        }else {
            Report report = reportMapper.getReportDetail(task.getReportId());
            if (report.getSourceType().equals(ReportSourceType.TEMP.toString())){
                // 删除临时调试数据
                debugDataMapper.deleteDebugData(report.getSourceId());
            }
        }
    }

    /**
     * 上传截图（支持云存储或本地存储）
     *
     * @param request // 引擎请求（fileName、base64String）
     * @return void   // 无返回
     */
    public void uploadScreenshot(EngineRequest request) {
        try{
            if(cloudStorage.equals("on")){
                UploadUtils.uploadImageB64(request.getFileName(), request.getBase64String(), uploadUrl, imageBucket, ak, sk);
            }else {
                String fileName = request.getFileName();
                String path = imagePath + "/" + fileName.split("_")[0] + "/" + fileName.split("_")[1];
                ImageUtils.convertBase64ToImage(request.getBase64String(), path);
            }
        } catch (Exception exception) {
            throw new LMException("截图文件上传失败");
        }
    }

    /**
     * 下载测试文件
     *
     * @param fileId   // 文件ID
     * @param response // 响应流
     * @return void    // 无返回
     */
    public void downloadTestFile(String fileId, HttpServletResponse response) {
        TestFile testFile = testFileMapper.getTestFile(fileId);
        FileUtils.downloadFile(testFile.getFilePath(), response);
    }

    /**
     * 下载应用安装包
     *
     * @param date        // 日期目录
     * @param fileId      // 文件ID
     * @param packageName // 包名
     * @param response    // 响应流
     * @return void       // 无返回
     */
    public void downloadAppPackage(String date, String fileId, String packageName, HttpServletResponse response) {
        String path = APP_PACKAGE_PATH + "/" + date + "/" + fileId + "/" + packageName;
        FileUtils.downloadFile(path, response);
    }

    /**
     * 预览截图
     *
     * @param date    // 日期目录
     * @param fileId  // 文件ID
     * @return ResponseEntity<byte[]> // 图片二进制响应
     */
    public ResponseEntity<byte[]> previewImage(String date, String fileId) {
        String path = imagePath + "/" + date + "/" + fileId;
        return FileUtils.previewImage(path);
    }

    /**
     * 下载任务打包文件（测试数据zip）
     *
     * @param taskId   // 任务ID
     * @param response // 响应流
     * @return void    // 无返回
     */
    public void downTaskFile(String taskId, HttpServletResponse response) {
        TaskDTO task = taskMapper.getTaskDetail(taskId);
        String taskZipPath = TASK_FILE_PATH+"/"+task.getProjectId()+"/"+task.getId()+".zip";
        FileUtils.downloadFile(taskZipPath, response);
    }

    /**
     * 发起执行测试计划（外部触发）
     *
     * @param request // 执行请求（planId、user、engineId、environmentId等）
     * @return String // 任务ID
     */
    public String execTestPlan(RunRequest request){
        Plan plan = planMapper.getPlanDetail(request.getPlanId());
        if(plan==null){
            throw new LMException("测试计划不存在");
        }
        User user = userMapper.getUser(request.getUser());
        if(user==null){
            throw new LMException("用户账号不存在");
        }

        request.setSourceId(request.getPlanId());
        request.setSourceType(ReportSourceType.PLAN.toString());
        request.setSourceName("【外部执行】"+ plan.getName());
        request.setTaskType(TaskType.API.toString());
        request.setRunUser(user.getId());
        if(request.getEnvironmentId()==null){
            request.setEnvironmentId(plan.getEnvironmentId());
        }
        if(request.getEngineId()==null){
            request.setEngineId(plan.getEngineId());
        }
        request.setProjectId(plan.getProjectId());
        TaskDTO task = runService.run(request);
        return task.getId();
    }

    /**
     * 获取计划执行报告
     *
     * @param taskId   // 任务ID
     * @return ReportDTO // 报告数据
     */
    public ReportDTO getPlanReport(String taskId){
        TaskDTO taskDTO = taskMapper.getTaskDetail(taskId);
        if(taskDTO==null){
            throw new LMException("测试任务不存在");
        }
        return reportService.getPlanResult(taskDTO.getReportId());
    }

}

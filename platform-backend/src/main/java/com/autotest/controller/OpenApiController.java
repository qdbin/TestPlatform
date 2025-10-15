package com.autotest.controller;

import com.autotest.dto.ReportDTO;
import com.autotest.request.EngineRequest;
import com.autotest.request.RunRequest;
import com.autotest.response.TaskResponse;
import com.autotest.service.OpenApiService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletResponse;

/**
 * 控制器：开放接口（引擎对接与外部触发）
 * 职责：提供引擎令牌、心跳、任务拉取与回传、附件下载、截图预览、外部触发计划执行等入口。
 */
@RestController
@RequestMapping("/openapi")
public class OpenApiController {

    @Resource
    private OpenApiService openApiService; // 开放接口服务

    /**
     * 申请引擎访问令牌
     * @param request 引擎请求载体
     * @return String 令牌或结果描述
     */
    @PostMapping("/engine/token/apply")
    public String applyEngineToken(@RequestBody EngineRequest request) {
        return openApiService.applyEngineToken(request);
    }

    /**
     * 引擎心跳上报
     * 功能：引擎端定期上报心跳，平台更新引擎在线状态与心跳时间
     *
     * @param request // 引擎请求载体（engineCode）
     * @return String // 心跳处理结果文案
     */
    @PostMapping("/engine/heartbeat/send")
    public String engineHeartbeat(@RequestBody EngineRequest request) {
        return openApiService.engineHeartbeat(request); // 委派至服务层处理心跳
    }

    /**
     * 引擎拉取待执行任务
     * 功能：引擎端请求获取待执行任务，可能返回调试数据或测试数据下载地址
     *
     * @param request // 引擎请求载体（engineCode）
     * @return TaskResponse // 任务响应（包含测试集合、调试数据或下载地址）
     */
    @PostMapping("/engine/task/fetch")
    public TaskResponse fetchEngineTask(@RequestBody EngineRequest request) {
        return openApiService.fetchEngineTask(request); // 委派任务拉取与数据构建
    }

    /**
     * 查询任务状态
     * 功能：引擎查询任务是否被平台标记终止，如终止则释放设备并返回停止标记
     *
     * @param request // 引擎请求载体（taskId）
     * @return String // "STOP" 表示终止，否则返回 null
     */
    @PostMapping("/engine/task/status")
    public String getTaskStatus(@RequestBody EngineRequest request) {
        return openApiService.getTaskStatus(request); // 委派状态查询与释放设备
    }

    /**
     * 上传用例执行结果
     * 功能：引擎回传用例结果，平台累计统计并更新报告数据
     *
     * @param request // 引擎请求载体（taskId、caseResultList）
     */
    @PostMapping("/engine/result/upload")
    public void uploadCaseResult(@RequestBody EngineRequest request) {
        openApiService.uploadCaseResult(request); // 写入报告统计
    }

    /**
     * 完成任务回调
     * 功能：引擎执行完成后回调，平台汇总报告状态、释放设备并进行通知
     *
     * @param request // 引擎请求载体（taskId、engineCode）
     */
    @PostMapping("/engine/task/complete")
    public void completeEngineTask(@RequestBody EngineRequest request) {
        openApiService.completeEngineTask(request); // 汇总报告并收尾
    }

    /**
     * 上传截图
     * 功能：引擎上传执行过程截图，平台进行本地或云端存储
     *
     * @param request // 引擎请求载体（taskId、imageBase64/路径等）
     */
    @PostMapping("/engine/screenshot/upload")
    public void uploadScreenshot(@RequestBody EngineRequest request) {
        openApiService.uploadScreenshot(request); // 委派截图存储
    }

    /**
     * 下载任务打包文件
     * 功能：提供任务执行所需测试数据的压缩包下载
     *
     * @param taskId   // 任务ID
     * @param response // 响应流
     */
    @GetMapping("/task/file/download/{taskId}")
    public void downloadTaskFile(@PathVariable String taskId, HttpServletResponse response) {
        openApiService.downTaskFile(taskId, response); // 输出下载流
    }

    /**
     * 下载测试文件
     * 功能：供引擎按 ID 拉取测试附件（如配置/脚本等）
     *
     * @param fileId   // 文件ID
     * @param response // 响应流
     */
    @GetMapping("/download/test/file/{fileId}")
    public void downloadTestFile(@PathVariable String fileId, HttpServletResponse response) {
        openApiService.downloadTestFile(fileId, response); // 输出文件内容
    }

    /**
     * 下载应用安装包
     * 功能：按日期/文件ID/包名下载 App 安装包
     *
     * @param date        // 日期目录
     * @param fileId      // 文件ID
     * @param packageName // 包名
     * @param response    // 响应流
     */
    @GetMapping("/download/package/{date}/{fileId}/{packageName}")
    public void downloadAppPackage(@PathVariable String date, @PathVariable String fileId,  @PathVariable String packageName, HttpServletResponse response) {
        openApiService.downloadAppPackage(date, fileId, packageName, response); // 输出安装包
    }

    /**
     * 预览截图
     * @param date    日期目录
     * @param imageId 图片ID
     * @return ResponseEntity<byte[]> 图片二进制响应
     */
    @GetMapping("/screenshot/{date}/{imageId}")
    public ResponseEntity<byte[]> previewImage(@PathVariable String date, @PathVariable String imageId) {
        return openApiService.previewImage(date, imageId);
    }

    /**
     * 外部触发执行测试计划
     * 功能：外部系统调用平台触发计划执行，返回任务ID
     *
     * @param request // 计划执行请求
     * @return String // 任务ID
     */
    @PostMapping("/exec/test/plan")
    public String execTestPlan(@RequestBody RunRequest request) {
        return openApiService.execTestPlan(request); // 委派计划执行
    }

    /**
     * 获取计划执行报告
     * 功能：根据任务ID返回聚合后的报告数据
     *
     * @param taskId // 任务ID
     * @return ReportDTO // 报告数据
     */
    @PostMapping("/exec/result/{taskId}")
    public ReportDTO getPlanReport(@PathVariable String taskId) {
        return openApiService.getPlanReport(taskId); // 委派报告查询
    }
}

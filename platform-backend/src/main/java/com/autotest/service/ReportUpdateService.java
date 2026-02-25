package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.autotest.common.constants.ReportStatus;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.dto.CollectionDTO;
import com.autotest.dto.TaskDTO;
import com.autotest.request.CaseResultRequest;
import com.autotest.request.TransResultRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
/**
 * 类型: Service
 * 职责: 根据执行结果更新测试报告，按集合/用例/事务维度入库并统计结果
 * 高频功能: (1) 创建/更新报告集合与用例明细 (2) 写入API/WEB/APP事务记录 (3) 汇总通过/失败/错误数量
 * 使用示例: updateReport(taskDTO, caseResultList)
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ReportUpdateService {

    @Value("${qiniu.cloud.downloadUrl}")
    private String downloadUrl;  // 七牛云加速域名

    @Value("${cloud.storage.on-off}")
    private String cloudStorage;  // 云存储开关

    @Resource
    private ReportMapper reportMapper;

    @Resource
    private CollectionMapper collectionMapper;

    @Resource
    private CollectionCaseMapper collectionCaseMapper;

    @Resource
    ReportCollectionMapper reportCollectionMapper;

    @Resource
    ReportCollectionCaseMapper reportCollectionCaseMapper;

    @Resource
    ReportCollectionCaseApiMapper reportCollectionCaseApiMapper;

    @Resource
    ReportCollectionCaseWebMapper reportCollectionCaseWebMapper;

    @Resource
    ReportCollectionCaseAppMapper reportCollectionCaseAppMapper;

    /**
     * 更新报告（支持批量用例结果）
     *
     * @param task            // 任务信息（含 reportId、来源等）
     * @param caseResultList  // 用例结果列表（含事务明细与状态）
     *
     * 主要思想：
     *      1. 遍历case_result
     *      2. 查询report_collection是否存在，不存在则创建并init
     *      3. 初始化report_collection，要判断是否存在collection_dto（只有collection/plan类型才存在），若存在要设置collection_name,collection_version,case_total
     */
    public void updateReport(TaskDTO task, List<CaseResultRequest> caseResultList) {
        // 遍历case_result,并持久化
        for(CaseResultRequest caseResult:caseResultList){
            // 查询or创建 report_collection
            ReportCollection reportCollection = reportCollectionMapper.getReportCollection(task.getReportId(), caseResult.getCollectionId());

            // 如果report_collection没有则创建（批次上传用例结果，可能存在有些用例的所属集合已存在或不存在的情况）
            if(reportCollection == null){
                // 查询集合详情 collection_dto（如果存在）
                CollectionDTO collection = collectionMapper.getCollectionDetail(caseResult.getCollectionId());

                // 新增 report_collection（第一次上传该集合下的用例结果，故report_collection需要创建并init）
                reportCollection = new ReportCollection();
                reportCollection.setId(UUID.randomUUID().toString());
                reportCollection.setReportId(task.getReportId());               // set report_id
                reportCollection.setCollectionId(caseResult.getCollectionId()); // set collection_id

                // collection/plan (collection_dto != null)
                if (collection !=null) {
                    reportCollection.setCollectionName(collection.getName());
                    reportCollection.setCollectionVersion(collection.getVersionName());
                    reportCollection.setCaseTotal(collectionCaseMapper.getCollectionCaseCount(caseResult.getCollectionId()));
                }
                // case/debug(collection_dto == null)
                else {
                    reportCollection.setCollectionName("");
                    reportCollection.setCollectionVersion("");
                    reportCollection.setCaseTotal(1);
                }

                reportCollectionMapper.addReportCollection(reportCollection); // 插入报告集合
            }

            // 构建report_collection_case
            ReportCollectionCase reportCollectionCase = new ReportCollectionCase();
            reportCollectionCase.setId(UUID.randomUUID().toString());
            reportCollectionCase.setReportCollectionId(reportCollection.getId());   //report_collection_id
            reportCollectionCase.setCollectionCaseIndex(caseResult.getIndex());     // collection_case_index
            reportCollectionCase.setCaseId(caseResult.getCaseId());                 // case_id
            reportCollectionCase.setCaseType(caseResult.getCaseType());             // case_type
            reportCollectionCase.setCaseName(caseResult.getCaseName());             // case_name
            reportCollectionCase.setCaseDesc(caseResult.getCaseDesc());
            reportCollectionCase.setStartTime(caseResult.getStartTime());           // start_time
            reportCollectionCase.setEndTime(caseResult.getEndTime());               // ent_time
            reportCollectionCase.setRunTimes(caseResult.getRunTimes());             // 执行次数
            reportCollectionCase.setDuring((caseResult.getEndTime()-caseResult.getStartTime()) + "ms"); // during=end_time-start_time
            reportCollectionCase.setStatus(getStatusByIndex(caseResult.getStatus())); // status（success/fail/error/skip）
            reportCollectionCaseMapper.addReportCollectionCase(reportCollectionCase); // 插入报告用例

            // 构建report_collection_case_api （提取事务明细，构建case_api结果记录）
            if(caseResult.getCaseType().equals("API")){
                // report_collection_case_api列表
                List<ReportCollectionCaseApi> reportCollectionCaseApiList = new ArrayList<>();

                // 遍历transaction_list事务明细，构建case_api结果记录
                for(int index=1; index <= caseResult.getTransactionList().size(); index++){
                    // 提取当前事务明细
                    TransResultRequest transactionResult =caseResult.getTransactionList().get(index-1);

                    // 构建对应report_collection_case_api
                    ReportCollectionCaseApi reportCollectionCaseApi = new ReportCollectionCaseApi();
                    reportCollectionCaseApi.setId(UUID.randomUUID().toString());
                    reportCollectionCaseApi.setReportCollectionCaseId(reportCollectionCase.getId());    // report_collection_case_id
                    reportCollectionCaseApi.setCaseApiIndex(index);                             // case_api_index（自己设置的顺序-估计是设置的展示）
                    reportCollectionCaseApi.setApiId(transactionResult.getId());                // api_id
                    reportCollectionCaseApi.setApiName(transactionResult.getName());            // api_name
                    reportCollectionCaseApi.setApiPath(transactionResult.getContent());         // api_path
                    reportCollectionCaseApi.setDescription(transactionResult.getDescription()); // case_api_description
                    reportCollectionCaseApi.setExecLog(transactionResult.getLog());             // exec_log
                    reportCollectionCaseApi.setDuring(transactionResult.getDuring());           // during
                    reportCollectionCaseApi.setStatus(getStatusByIndex(transactionResult.getStatus())); // status
                    reportCollectionCaseApiList.add(reportCollectionCaseApi);
                }
                reportCollectionCaseApiMapper.batchAddReportCollectionCaseApi(reportCollectionCaseApiList); // 批量插入API事务
            }

            // web
            else if(caseResult.getCaseType().equals("WEB")){
                List<ReportCollectionCaseWeb> reportCollectionCaseWebList = new ArrayList<>();
                for(int index=1; index <= caseResult.getTransactionList().size(); index++){
                    TransResultRequest transactionResult =caseResult.getTransactionList().get(index-1);
                    ReportCollectionCaseWeb reportCollectionCaseWeb = new ReportCollectionCaseWeb();
                    reportCollectionCaseWeb.setId(UUID.randomUUID().toString());
                    reportCollectionCaseWeb.setReportCollectionCaseId(reportCollectionCase.getId());
                    reportCollectionCaseWeb.setCaseWebIndex(index);
                    reportCollectionCaseWeb.setOperationId(transactionResult.getId());
                    reportCollectionCaseWeb.setOperationName(transactionResult.getName());
                    reportCollectionCaseWeb.setOperationElement(transactionResult.getContent());
                    reportCollectionCaseWeb.setDescription(transactionResult.getDescription());
                    reportCollectionCaseWeb.setExecLog(transactionResult.getLog());
                    List<String> screenshot = new ArrayList<>();
                    for(String screenshotId:transactionResult.getScreenShotList()){
                        String url;
                        if(cloudStorage.equals("on")){
                            url = downloadUrl + "/" + screenshotId + ".png";
                        }else {
                            url = "/openapi/screenshot/" + screenshotId.split("_")[0] +
                                    "/" + screenshotId.split("_")[1] + ".png";
                        }
                        screenshot.add(url); // 收集截图URL
                    }
                    reportCollectionCaseWeb.setScreenshot(JSONArray.toJSONString(screenshot));
                    reportCollectionCaseWeb.setStatus(getStatusByIndex(transactionResult.getStatus()));
                    reportCollectionCaseWebList.add(reportCollectionCaseWeb);
                }
                reportCollectionCaseWebMapper.batchAddReportCollectionCaseWeb(reportCollectionCaseWebList); // 批量插入WEB事务
            }

            // app
            else {
                List<ReportCollectionCaseApp> reportCollectionCaseAppList = new ArrayList<>();
                for(int index=1; index <= caseResult.getTransactionList().size(); index++){
                    TransResultRequest transactionResult =caseResult.getTransactionList().get(index-1);
                    ReportCollectionCaseApp reportCollectionCaseApp = new ReportCollectionCaseApp();
                    reportCollectionCaseApp.setId(UUID.randomUUID().toString());
                    reportCollectionCaseApp.setReportCollectionCaseId(reportCollectionCase.getId());
                    reportCollectionCaseApp.setCaseAppIndex(index);
                    reportCollectionCaseApp.setOperationId(transactionResult.getId());
                    reportCollectionCaseApp.setOperationName(transactionResult.getName());
                    reportCollectionCaseApp.setOperationElement(transactionResult.getContent());
                    reportCollectionCaseApp.setDescription(transactionResult.getDescription());
                    reportCollectionCaseApp.setExecLog(transactionResult.getLog());
                    List<String> screenshot = new ArrayList<>();
                    for(String screenshotId:transactionResult.getScreenShotList()){
                        String url;
                        if(cloudStorage.equals("on")){
                            url = downloadUrl + "/" + screenshotId + ".png";
                        }else {
                            url = "/openapi/screenshot/" + screenshotId.split("_")[0] +
                                    "/" + screenshotId.split("_")[1] + ".png";
                        }
                        screenshot.add(url); // 收集截图URL
                    }
                    reportCollectionCaseApp.setScreenshot(JSONArray.toJSONString(screenshot));
                    reportCollectionCaseApp.setStatus(getStatusByIndex(transactionResult.getStatus()));
                    reportCollectionCaseAppList.add(reportCollectionCaseApp);
                }
                reportCollectionCaseAppMapper.batchAddReportCollectionCaseApp(reportCollectionCaseAppList); // 批量插入APP事务
            }
        }

        // 更新report_endTime和report_updateTime
        reportMapper.updateReportEndTime(task.getReportId(), System.currentTimeMillis(), System.currentTimeMillis());
        // 统计报告 后续可job统计
        this.statisticsReport(task.getReportId());
    }

    /**
     * 统计报告整体结果（成功/失败/错误计数）
     *
     * @param reportId // 报告ID
     */
    public void statisticsReport(String reportId){
        // 查询对应report_collection对应case用例的执行结果
        Integer passCount = reportCollectionCaseMapper.countReportResult(ReportStatus.SUCCESS.toString(), reportId);
        Integer failCount = reportCollectionCaseMapper.countReportResult(ReportStatus.FAIL.toString(), reportId);
        Integer errorCount = reportCollectionCaseMapper.countReportResult(ReportStatus.ERROR.toString(), reportId);

        // 更新report_statistics的pass_count,fail_count,error_count
        ReportStatistics reportStatistics = reportMapper.getReportStatistics(reportId);     // 根据report_id获得report_statistics
        reportStatistics.setPassCount(passCount);
        reportStatistics.setFailCount(failCount);
        reportStatistics.setErrorCount(errorCount);
        reportMapper.updateReportStatistics(reportStatistics); // 更新统计信息
    }

    /**
     * 将状态索引转换为报告状态枚举名称
     *
     * @param status // 状态索引: 0成功,1失败,2错误,其他跳过
     * @return String // 枚举名称: SUCCESS/FAIL/ERROR/SKIP
     */
    private String getStatusByIndex(Integer status) {
        if(status == 0){
            return ReportStatus.SUCCESS.toString();
        }else if (status == 1){
            return ReportStatus.FAIL.toString();
        }else if (status == 2){
            return ReportStatus.ERROR.toString();
        }else {
            return ReportStatus.SKIP.toString();
        }
    }

}

package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.ReportStatus;
import com.autotest.domain.Report;
import com.autotest.mapper.*;
import com.autotest.dto.ReportCollectionCaseDTO;
import com.autotest.dto.ReportCollectionCaseTransDTO;
import com.autotest.dto.ReportCollectionDTO;
import com.autotest.dto.ReportDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;

@Service
@Transactional(rollbackFor = Exception.class)
/**
 * 服务：报告查询与维护
 * 
 *     职责：提供报告删除、列表查询、最新接口调试结果解析、用例/计划执行结果汇总。
 *     关键点：
 *         - 删除报告需级联清理各端（API/WEB/App）动作与集合、用例记录
 *         - 列表查询对条件进行通配包装以支持模糊匹配
 *         - 最新接口报告解析从HTML片段中提取响应体并安全JSON化
 *         - 计划结果汇总时统计每集合通过/失败/错误数据
 */
public class ReportService {

    @Resource
    private ReportMapper reportMapper;

    @Resource
    private ReportCollectionMapper reportCollectionMapper;

    @Resource
    private ReportCollectionCaseMapper reportCollectionCaseMapper;

    @Resource
    private ReportCollectionCaseApiMapper reportCollectionCaseApiMapper;

    @Resource
    private ReportCollectionCaseWebMapper reportCollectionCaseWebMapper;

    @Resource
    private ReportCollectionCaseAppMapper reportCollectionCaseAppMapper;

    /**
     * 删除报告（级联删除各端动作与集合/用例）
     * 
     *     @param report // 报告实体（使用id）
     *     @return void // 无返回
     */
    public void deleteReport(Report report) {
        reportCollectionCaseAppMapper.deleteByReportId(report.getId());
        reportCollectionCaseApiMapper.deleteByReportId(report.getId());
        reportCollectionCaseWebMapper.deleteByReportId(report.getId());
        reportCollectionCaseMapper.deleteByReportId(report.getId());
        reportCollectionMapper.deleteByReportId(report.getId());
        reportMapper.deleteReport(report.getId());
    }

    /**
     * 分页查询报告列表（模糊条件）
     * 
     *     @param request          // 查询请求（项目/条件/状态/时间范围）
     *     @return List<ReportDTO> // 报告列表
     */
    public List<ReportDTO> getReportList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition(("%"+request.getCondition()+"%"));
        }
        return reportMapper.getReportList(request);
    }

    /**
     * 获取接口最新调试报告响应体
     * 
     *     @param apiId       // 接口ID
     *     @return JSONObject // 响应体JSON；解析失败返回空对象或null
     * 
     *     说明：从存储的HTML片段中定位“响应体”标记并截取，随后进行安全解析。
     */
    public JSONObject getLastApiReport(String apiId){
        JSONObject result = new JSONObject();
        String report = reportCollectionCaseApiMapper.getLastApiReport(apiId);
        if(report == null){
            return null;
        }
        if(!report.contains("<br><b>响应体: ") || !report.contains("</b><br><br>")){
            return null;
        }
        String response = report.substring(report.indexOf("<br><b>响应体: ")+12, report.indexOf("</b><br><br>"));
        try{
            result = JSONObject.parseObject(response);
        }catch (Exception e){
            return result;
        }
        return result;
    }

    /**
     * 获取单个用例调试执行结果
     * 
     *     @param taskId                         // 任务ID
     *     @return ReportCollectionCaseDTO       // 用例执行结果（含步骤事务列表）
     */
    public ReportCollectionCaseDTO getCaseResult(String taskId){
        ReportCollectionCaseDTO reportCase = reportCollectionCaseMapper.getCaseReportByTaskId(taskId);
        if(reportCase != null){
            List<ReportCollectionCaseTransDTO> transList;
            if(reportCase.getCaseType().equals("API")){
                transList = reportCollectionCaseApiMapper.getReportCaseActionList(reportCase.getId());
            }else if(reportCase.getCaseType().equals("WEB")){
                transList = reportCollectionCaseWebMapper.getReportCaseActionList(reportCase.getId());
            }else {
                transList = reportCollectionCaseAppMapper.getReportCaseActionList(reportCase.getId());
            }
            reportCase.setTransList(transList);
        }

        return reportCase;
    }

    /**
     * 获取计划执行结果汇总
     * 
     *     @param reportId    // 报告ID
     *     @return ReportDTO  // 报告详情（集合与用例事务，含统计）
     */
    public ReportDTO getPlanResult(String reportId){
        ReportDTO report = reportMapper.getReportDetail(reportId);
        List<ReportCollectionDTO> reportCollectionList = reportCollectionMapper.getReportCollectionList(reportId);
        for(ReportCollectionDTO reportCollection:reportCollectionList){
            List<ReportCollectionCaseDTO> reportCollectionCaseList = reportCollectionCaseMapper.getReportCollectionCaseList(reportCollection.getId());
            for(ReportCollectionCaseDTO reportCollectionCase: reportCollectionCaseList){
                List<ReportCollectionCaseTransDTO> transList;
                if(reportCollectionCase.getCaseType().equals("API")){
                    transList = reportCollectionCaseApiMapper.getReportCaseActionList(reportCollectionCase.getId());
                }else if(reportCollectionCase.getCaseType().equals("WEB")){
                    transList = reportCollectionCaseWebMapper.getReportCaseActionList(reportCollectionCase.getId());
                }else {
                    transList = reportCollectionCaseAppMapper.getReportCaseActionList(reportCollectionCase.getId());
                }
                reportCollectionCase.setTransList(transList);
            }
            reportCollection.setCaseList(reportCollectionCaseList);
            Integer passCount = reportCollectionCaseMapper.countReportCollectionResult(ReportStatus.SUCCESS.toString(), reportCollection.getId());
            Integer failCount = reportCollectionCaseMapper.countReportCollectionResult(ReportStatus.FAIL.toString(), reportCollection.getId());
            Integer errorCount = reportCollectionCaseMapper.countReportCollectionResult(ReportStatus.ERROR.toString(), reportCollection.getId());
            reportCollection.setPassCount(passCount);
            reportCollection.setFailCount(failCount);
            reportCollection.setErrorCount(errorCount);
        }
        report.setCollectionList(reportCollectionList);
        return report;
    }
}

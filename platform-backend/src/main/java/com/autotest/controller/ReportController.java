package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Report;
import com.autotest.dto.ReportCollectionCaseDTO;
import com.autotest.dto.ReportDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.ReportService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 控制层：报告管理入口
 * 职责：调试报告查询、计划报告查询、删除与分页列表
 * 示例：入口函数 getReportList -> PageHelper.startPage -> ReportService.getReportList
 */
@RestController
@RequestMapping("/autotest/report")
public class ReportController {

    @Resource
    private ReportService reportService;

    /**
     * 获取调试用例执行结果
     * 
     *     @param taskId                         // 任务ID
     *     @return ReportCollectionCaseDTO       // 单个用例执行结果（含步骤事务列表）
     */
    @GetMapping("/debug/{taskId}")
    public ReportCollectionCaseDTO getCaseResult(@PathVariable String taskId){
        return reportService.getCaseResult(taskId);
    }

    /**
     * 获取计划执行结果
     * 
     *     @param reportId          // 报告ID
     *     @return ReportDTO        // 报告详情（含各集合与用例统计）
     */
    @GetMapping("/run/{reportId}")
    public ReportDTO getPlanResult(@PathVariable String reportId){
        return reportService.getPlanResult(reportId);
    }

    /**
     * 删除报告
     * 
     *     @param report   // 报告实体（使用id删除）
     *     @return void    // 无返回
     */
    @PostMapping("/delete")
    public void deleteReport(@RequestBody Report report) {
        reportService.deleteReport(report);
    }

    /**
     * 分页查询报告列表
     * 
     *     @param goPage            // 页码
     *     @param pageSize          // 页大小
     *     @param request           // 查询请求（项目/条件/状态/时间范围）
     *     @return Pager<List<ReportDTO>> // 分页封装的报告列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<ReportDTO>> getReportList(@PathVariable int goPage, @PathVariable int pageSize,
                                                     @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, reportService.getReportList(request));
    }

}

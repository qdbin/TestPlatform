package com.autotest.controller;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.dto.CaseDTO;
import com.autotest.request.ApiParamRuleRequest;
import com.autotest.request.CaseRequest;
import com.autotest.request.QueryRequest;
import com.autotest.service.CaseGenerateService;
import com.autotest.service.CaseService;
import com.autotest.service.ReportService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制层：用例管理入口
 * 
 *     职责简述：提供用例保存、删除、详情、系统类型查询与分页列表的HTTP接口。
 *     说明：参数透传至Service层，控制器负责轻量的用户上下文注入与分页包装。
 */
@RestController
@RequestMapping("/autotest/case")
public class CaseController {

    @Resource
    private CaseService caseService;

    @Resource
    private ReportService reportService;

    @Resource
    private CaseGenerateService caseGenerateService;

    /**
     * 保存用例
     * 
     *     @param caseRequest // 用例请求（含基础信息与分类型步骤）
     *     @param request     // Http请求上下文（用于注入更新人）
     *     @return void       // 无返回
     */
    @PostMapping("/save")
    public void saveCase(@RequestBody CaseRequest caseRequest, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        caseRequest.setUpdateUser(user);
        caseService.saveCase(caseRequest);
    }

    /**
     * 删除用例
     * 
     *     @param request // 用例请求（使用id）
     *     @return void   // 无返回
     */
    @PostMapping("/delete")
    public void deleteCase(@RequestBody CaseRequest request) {
        caseService.deleteCase(request);
    }

    /**
     * 获取用例详情
     * 
     *     @param caseType // 用例类型（API/WEB/android/apple）
     *     @param caseId   // 用例ID
     *     @return CaseDTO // 用例扩展DTO（含步骤列表、元素/控件信息）
     */
    @GetMapping("/detail/{caseType}/{caseId}")
    public CaseDTO getCaseDetail(@PathVariable String caseType, @PathVariable String caseId){
        return caseService.getCaseDetail(caseType, caseId);
    }

    /**
     * 查询用例系统类型
     * 
     *     @param caseId  // 用例ID
     *     @return String // 系统类型（web/app/android/apple等）
     */
    @GetMapping("/system/{caseId}")
    public String getCaseSystem(@PathVariable String caseId){
        return caseService.getCaseSystem(caseId);
    }

    /**
     * 分页查询用例列表
     * 
     *     说明：使用分页助手进行分页，透传模糊条件与筛选，返回分页信息包装的列表。
     * 
     *     @param goPage   // 目标页码
     *     @param pageSize // 每页条数
     *     @param request  // 查询请求（项目ID、模块、类型、系统、模糊条件）
     *     @return Pager<List<CaseDTO>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<CaseDTO>> getCaseList(@PathVariable int goPage, @PathVariable int pageSize,@RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, caseService.getCaseList(request));
    }

    @GetMapping("/api/report/{apiId}")
    public JSONObject getLastApiReport(@PathVariable String apiId){
        return reportService.getLastApiReport(apiId);
    }

    @PostMapping("/auto/generate")
    public void generateCase(@RequestBody ApiParamRuleRequest ruleRequest, HttpServletRequest request){
        String user = request.getSession().getAttribute("userId").toString();
        ruleRequest.setCreateUser(user);
        caseGenerateService.generateCase(ruleRequest);
    }
}

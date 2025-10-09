package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.PlanNotice;
import com.autotest.dto.PlanDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.PlanService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：测试计划入口
 * 职责：计划保存/删除、通知配置、详情与分页列表
 */
@RestController
@RequestMapping("/autotest/plan")
public class PlanController {

    @Resource
    private PlanService planService;

    /**
     * 功能：保存测试计划
     *
     * @param planDTO  // 计划DTO
     * @param request  // Http请求上下文（注入更新人）
     * @return void    // 无返回
     */
    @PostMapping("/save")
    public void savePlan(@RequestBody PlanDTO planDTO, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        planDTO.setUpdateUser(user);
        planService.savePlan(planDTO);
    }

    /**
     * 功能：保存计划通知配置
     *
     * @param planNotice // 通知配置实体
     * @return void      // 无返回
     */
    @PostMapping("/save/notice")
    public void savePlanNotice(@RequestBody PlanNotice planNotice) {
        planService.savePlanNotice(planNotice);
    }

    /**
     * 功能：删除测试计划
     *
     * @param planDTO // 计划DTO（仅使用id）
     * @return void   // 无返回
     */
    @PostMapping("/delete")
    public void deletePlan(@RequestBody PlanDTO planDTO) {
        planService.deletePlan(planDTO);
    }

    /**
     * 功能：查询计划通知配置
     *
     * @param planId // 计划ID
     * @return PlanNotice // 通知配置
     */
    @GetMapping("/notice/{planId}")
    public PlanNotice getPlanNotice(@PathVariable String planId){
        return planService.getPlanNotice(planId);
    }

    /**
     * 功能：查询计划详情
     *
     * @param planId // 计划ID
     * @return PlanDTO // 计划详情
     */
    @GetMapping("/detail/{planId}")
    public PlanDTO getPlanDetail(@PathVariable String planId){
        return planService.getPlanDetail(planId);
    }

    /**
     * 功能：分页查询计划列表
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询请求
     * @return Pager<List<PlanDTO>> // 分页封装的计划列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<PlanDTO>> getPlanList(@PathVariable int goPage, @PathVariable int pageSize,
                                           @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, planService.getPlanList(request));
    }
}

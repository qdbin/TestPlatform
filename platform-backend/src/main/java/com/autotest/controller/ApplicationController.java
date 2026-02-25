package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Application;
import com.autotest.request.QueryRequest;
import com.autotest.service.ApplicationService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 控制器：应用管理入口
 * 职责：保存、删除应用；按系统类型与分页列表查询。
 */
@RestController
@RequestMapping("/autotest/application")
public class ApplicationController {

    @Resource
    private ApplicationService applicationService;

    /**
     * 保存应用（新增或更新）
     *
     * @param application // 应用实体
     * @return void       // 无返回
     */
    @PostMapping("/save")
    public void saveApplication(@RequestBody Application application) {
        applicationService.saveApplication(application);
    }

    /**
     * 删除应用
     *
     * @param application // 应用实体（仅使用id）
     * @return void       // 无返回
     */
    @PostMapping("/delete")
    public void deleteApplication(@RequestBody Application application) {
        applicationService.deleteApplication(application.getId());
    }

    /**
     * 按系统类型查询应用列表
     *
     * @param system     // 系统类型（android/apple/web等）
     * @param projectId  // 项目ID
     * @return List<Application> // 应用列表
     */
    @GetMapping("/list/{system}/{projectId}")
    public List<Application> getApplicationList(@PathVariable String system, @PathVariable String projectId) {
        return applicationService.getApplicationList(projectId, null, system);
    }

    /**
     * 分页查询应用列表
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询条件（项目/关键字）
     * @return Pager<List<Application>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<Application>> getApplicationPageList(@PathVariable int goPage, @PathVariable int pageSize,
                                                      @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, applicationService.getApplicationList(request.getProjectId(), request.getCondition(), null));
    }
}

package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Environment;
import com.autotest.dto.EnvironmentDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.EnvironmentService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：环境管理入口
 * 职责：保存、删除、查询全部环境与分页列表
 */
@RestController
@RequestMapping("/autotest/environment")
public class EnvironmentController {

    @Resource
    private EnvironmentService environmentService;

    /**
     * 功能：保存环境（新增或更新）
     *
     * @param environment // 环境实体
     * @param request     // Http请求上下文（注入更新人）
     * @return void       // 无返回
     */
    @PostMapping("/save")
    public void saveEnvironment(@RequestBody Environment environment, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        environment.setUpdateUser(user);
        environmentService.saveEnvironment(environment);
    }

    /**
     * 功能：删除环境
     *
     * @param environment // 环境实体（仅使用id）
     * @return void       // 无返回
     */
    @PostMapping("/delete")
    public void deleteEnvironment(@RequestBody Environment environment) {
        environmentService.deleteEnvironment(environment);
    }

    /**
    * 功能：查询项目下所有环境
    *
    * @param projectId // 项目ID
    * @return List<Environment> // 环境列表
    */
    @GetMapping("/all/{projectId}")
    public List<Environment> getAllEnvironment(@PathVariable String projectId) {
        return environmentService.getAllEnvironment(projectId);
    }

    /**
    * 功能：分页查询环境列表
    *
    * @param goPage    // 页码
    * @param pageSize  // 每页大小
    * @param request   // 查询请求（projectId/condition）
    * @return Pager<List<EnvironmentDTO>> // 分页封装的环境列表
    */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<EnvironmentDTO>> getEnvironmentList(@PathVariable int goPage, @PathVariable int pageSize,
                                                          @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, environmentService.getEnvironmentList(request.getProjectId(), request.getCondition()));
    }

}

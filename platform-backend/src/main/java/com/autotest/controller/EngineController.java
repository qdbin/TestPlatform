package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Engine;
import com.autotest.domain.Task;
import com.autotest.dto.EngineDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.EngineService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：执行引擎入口
 * 职责：注册/删除引擎、停止任务、详情与分页列表
 */
@RestController
@RequestMapping("/autotest/engine")
public class EngineController {

    @Resource
    private EngineService engineService;

    /**
     * 功能：注册或更新引擎
     *
     * @param engine  // 引擎实体
     * @param request // Http请求上下文（注入更新人）
     * @return Engine // 保存后的引擎信息
     */
    @PostMapping("/register")
    public Engine saveEngine(@RequestBody Engine engine, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        engine.setUpdateUser(user);
        return engineService.saveEngine(engine);
    }

    /**
     * 功能：删除引擎
     *
     * @param engine // 引擎实体（仅使用id）
     * @return void  // 无返回
     */
    @PostMapping("/delete")
    public void deleteEngine(@RequestBody Engine engine) {
        engineService.deleteEngine(engine);
    }

    /**
     * 功能：停止引擎上的指定任务
     *
     * @param task // 任务实体（含任务id）
     * @return void // 无返回
     */
    @PostMapping("/stop/task")
    public void stopEngineTask(@RequestBody Task task) {
        engineService.stopEngineTask(task);
    }

    /**
     * 功能：停止引擎上所有任务
     *
     * @param engine // 引擎实体（仅使用id）
     * @return void  // 无返回
     */
    @PostMapping("/stop/all/task")
    public void stopEngineAllTask(@RequestBody Engine engine) {
        engineService.stopEngineAllTask(engine.getId());
    }

    /**
     * 功能：查询项目下所有自定义引擎
     *
     * @param projectId // 项目ID
     * @return List<Engine> // 引擎列表
     */
    @GetMapping("/all/{projectId}")
    public List<Engine> getAllCustomEngine(@PathVariable String projectId) {
        return engineService.getAllCustomEngine(projectId);
    }

    /**
     * 功能：查询引擎详情
     *
     * @param engineId // 引擎ID
     * @return EngineDTO // 引擎详情
     */
    @GetMapping("/detail/{engineId}")
    public EngineDTO getEngineDetail(@PathVariable String engineId) {
        return engineService.getEngineById(engineId);
    }

    /**
     * 功能：分页查询引擎列表
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询请求
     * @return Pager<List<EngineDTO>> // 分页封装的引擎列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<EngineDTO>> getEnvironmentList(@PathVariable int goPage, @PathVariable int pageSize,
                                                     @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, engineService.getEngineList(request.getProjectId(), request.getCondition()));
    }

}

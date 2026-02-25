package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Driver;
import com.autotest.request.QueryRequest;
import com.autotest.service.DriverService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 控制器：驱动配置入口
 * 职责：保存、删除、项目驱动查询与分页列表
 */
@RestController
@RequestMapping("/autotest/driver")
public class DriverController {

    @Resource
    private DriverService driverService;

    /**
     * 功能：保存驱动配置
     *
     * @param driver // 驱动实体
     * @return void  // 无返回
     */
    @PostMapping("/save")
    public void saveDriver(@RequestBody Driver driver) {
        driverService.saveDriver(driver);
    }

    /**
     * 功能：删除驱动配置
     *
     * @param driver // 驱动实体（仅使用id）
     * @return void  // 无返回
     */
    @PostMapping("/delete")
    public void deleteDriver(@RequestBody Driver driver) {
        driverService.deleteDriver(driver.getId());
    }

    /**
     * 功能：查询项目下所有驱动
     *
     * @param projectId // 项目ID
     * @return List<Driver> // 驱动列表
     */
    @GetMapping("/list/{projectId}")
    public List<Driver> getDriverList(@PathVariable String projectId) {
        return driverService.getDriverList(projectId, null);
    }

    /**
     * 功能：分页查询驱动列表
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询请求
     * @return Pager<List<Driver>> // 分页封装的驱动列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<Driver>> getDriverPageList(@PathVariable int goPage, @PathVariable int pageSize,
                                                      @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, driverService.getDriverList(request.getProjectId(), request.getCondition()));
    }
}

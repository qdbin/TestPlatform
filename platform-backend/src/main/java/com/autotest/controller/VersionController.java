package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Version;
import com.autotest.request.QueryRequest;
import com.autotest.service.VersionService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;


/**
 * 控制器：版本管理入口
 * 职责：提供版本的保存、删除、列表与分页查询接口。
 */
@RestController
@RequestMapping("/autotest/version")
public class VersionController {

    @Resource
    private VersionService versionService;

    /**
     * 保存版本（新增或更新）
     *
     * @param version // 版本实体
     * @return void   // 无返回
     */
    @PostMapping("/save")
    public void saveVersion(@RequestBody Version version) {
        versionService.saveVersion(version);
    }

    /**
     * 删除版本（逻辑删除）
     *
     * @param version // 版本实体（仅使用id）
     * @return void   // 无返回
     */
    @PostMapping("/delete")
    public void deleteVersion(@RequestBody Version version) {
        versionService.deleteVersion(version.getId());
    }

    /**
     * 查询项目下版本列表
     *
     * @param projectId     // 项目ID
     * @return List<Version> // 版本列表
     */
    @GetMapping("/list/{projectId}")
    public List<Version> getVersionList(@PathVariable String projectId) {
        return versionService.getVersionList(projectId, null);
    }

    /**
     * 分页查询版本列表
     *
     * 说明：统一使用 PageHelper 进行分页拦截，返回 Pager。
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询条件（项目ID与模糊条件）
     * @return Pager<List<Version>> // 分页信息与版本列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<Version>> getVersionPageList(@PathVariable int goPage, @PathVariable int pageSize,
                                                      @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, versionService.getVersionList(request.getProjectId(), request.getCondition()));
    }
}

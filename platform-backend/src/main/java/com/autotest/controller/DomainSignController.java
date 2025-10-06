package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.DomainSign;
import com.autotest.request.QueryRequest;
import com.autotest.service.DomainSignService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;


/**
 * 控制器：DomainSign 域标识管理入口
 * 职责：提供域标识的创建、删除、列表与分页查询接口。
 */
@RestController
@RequestMapping("/autotest/domainSign")
public class DomainSignController {

    @Resource
    private DomainSignService domainSignService;

    /**
     * 新增或更新域标识
     *
     * @param domainSign // 域标识实体
     * @return void      // 无返回
     */
    @PostMapping("/save")
    public void saveDomainSign(@RequestBody DomainSign domainSign) {
        domainSignService.saveDomainSign(domainSign);
    }

    /**
     * 删除域标识（逻辑删除）
     *
     * @param domainSign // 域标识实体（仅使用id）
     * @return void      // 无返回
     */
    @PostMapping("/delete")
    public void deleteDomainSign(@RequestBody DomainSign domainSign) {
        domainSignService.deleteDomainSign(domainSign.getId());
    }

    /**
     * 根据项目查询域标识列表
     *
     * @param projectId       // 项目ID
     * @return List<DomainSign> // 域标识列表
     */
    @GetMapping("/list/{projectId}")
    public List<DomainSign> getDomainSignList(@PathVariable String projectId) {
        return domainSignService.getDomainSignList(projectId, null);
    }

    /**
     * 分页查询域标识列表
     *
     * 说明：统一使用 PageHelper 进行分页拦截，返回 Pager。
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询条件（项目ID与模糊条件）
     * @return Pager<List<DomainSign>> // 分页信息与数据列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<DomainSign>> getDomainSignPageList(@PathVariable int goPage, @PathVariable int pageSize,
                                                   @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, domainSignService.getDomainSignList(request.getProjectId(), request.getCondition()));
    }
}

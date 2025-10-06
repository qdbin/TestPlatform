package com.autotest.controller;

import com.autotest.domain.Domain;
import com.autotest.dto.DomainDTO;
import com.autotest.service.DomainService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制器：域配置接口
 *     职责：保存；删除；列表查询
 */
@RestController
@RequestMapping("/autotest/domain")
public class DomainController {

    @Resource
    private DomainService domainService;

    /**
     * 保存域配置
     *
     * @param domain   // 域实体
     * @return void    // 无返回
     */
    @PostMapping("/save")
    public void saveDomain(@RequestBody Domain domain, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        domain.setUpdateUser(user); // 设置更新人
        domainService.saveDomain(domain); // 委托服务保存
    }

    /**
     * 删除域配置
     *
     * @param domain   // 域实体（包含id）
     * @return void    // 无返回
     */
    @PostMapping("/delete")
    public void deleteEnvironment(@RequestBody Domain domain) {
        domainService.deleteDomain(domain); // 委托服务删除
    }

    /**
     * 获取环境下域配置列表
     *
     * @param environmentId // 环境ID
     * @return List<DomainDTO> // 列表
     */
    @GetMapping("/list/{environmentId}")
    public List<DomainDTO> getDomainList(@PathVariable String environmentId) {
        return domainService.getDomainList(environmentId); // 委托服务查询
    }

}

package com.autotest.controller;

import com.autotest.domain.Assertion;
import com.autotest.service.SystemService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 控制器：系统配置相关入口
 * 职责：提供断言列表等系统级配置信息查询接口。
 */
@RestController
@RequestMapping("/autotest/system")
public class SystemController {

    @Resource
    private SystemService systemService;

    /**
     * 查询断言规则列表
     *
     * @return List<Assertion> // 系统内置或配置的断言列表
     */
    @GetMapping("/assertion/list")
    public List<Assertion> getAssertion() {
        return systemService.getAssertion();
    }

}

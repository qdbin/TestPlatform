package com.autotest.service;

import com.autotest.domain.Assertion;
import com.autotest.mapper.AssertionMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;

/**
 * 服务：系统字典与通用配置
 * 职责：提供断言规则等系统级配置的查询。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class SystemService {

    @Resource
    private AssertionMapper assertionMapper;

    /**
     * 查询断言规则
     *
     * @return List<Assertion> // 系统内置断言列表
     */
    public List<Assertion> getAssertion() {
        return assertionMapper.getAssertion();
    }

}

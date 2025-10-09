package com.autotest.mapper;

import com.autotest.domain.Assertion;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 类：AssertionMapper（断言配置持久层）
 * 职责：提供断言集合的读取接口（mapper）
 */
@Mapper
public interface AssertionMapper {
    /**
     * 获取所有断言配置（函数功能）
     *
     * @return List<Assertion> // 断言列表
     *
     * 示例：assertionMapper.getAssertion() -> 返回断言集合
     */
    List<Assertion> getAssertion();
}
package com.autotest.mapper;

import com.autotest.domain.Domain;
import com.autotest.dto.DomainDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：域配置数据访问（CRUD:Domain）
 * 用途：持久化域配置并提供查询接口
 */
@Mapper
public interface DomainMapper {
    /**
     * 保存域配置（新增或更新）
     *
     * @param domain    // 域实体数据（包含环境/键/值等）
     * @return void     // 无返回，落库成功即完成
     *
     * 示例：
     *     入参：domain.id为空表示新增
     *     调用：domainMapper.saveDomain(domain)
     *     返回：无
     */
    void saveDomain(Domain domain);

    /**
     * 删除域配置
     *
     * @param id        // 主键ID
     * @return void     // 无返回
     */
    void deleteDomain(String id);

    /**
     * 根据环境与键获取域配置
     *
     * @param environmentId // 环境ID
     * @param domainKey     // 键（匹配标识）
     * @return Domain       // 匹配到的域配置
     */
    Domain getDomainByName(String environmentId, String domainKey);

    /**
     * 获取环境下路径匹配的域配置列表
     *
     * @param environmentId // 环境ID
     * @return List<Domain> // 域配置列表
     */
    List<Domain> getPathDomainList(String environmentId);

    /**
     * 获取环境下域配置列表（含扩展字段）
     *
     * @param environmentId   // 环境ID
     * @return List<DomainDTO> // 域配置列表（DTO）
     */
    List<DomainDTO> getDomainList(String environmentId);

}
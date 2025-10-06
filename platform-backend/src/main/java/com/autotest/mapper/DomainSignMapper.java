package com.autotest.mapper;

import com.autotest.domain.DomainSign;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 类：DomainSignMapper（域名签名持久层）
 * 职责：管理域名签名增删查接口（mapper）
 */
@Mapper
public interface DomainSignMapper {
    /**
     * 保存域名签名记录（函数功能）
     *
     * @param domainSign // 域名签名实体
     *
     * 示例：domainSignMapper.saveDomainSign(entity)
     */
    void saveDomainSign(DomainSign domainSign);

    /**
     * 删除域名签名记录（函数功能）
     *
     * @param id // 记录ID
     *
     * 示例：domainSignMapper.deleteDomainSign(id)
     */
    void deleteDomainSign(String id);

    /**
     * 按名称查询域名签名（函数功能）
     *
     * @param projectId // 项目ID
     * @param name      // 域名签名名称
     * @return DomainSign // 匹配的域名签名
     *
     * 示例：domainSignMapper.getDomainSignByName(projectId, "api")
     */
    DomainSign getDomainSignByName(String projectId, String name);

    /**
     * 查询域名签名列表（支持条件过滤）
     *
     * @param projectId // 项目ID
     * @param condition // 过滤条件（可空）
     * @return List<DomainSign> // 域名签名列表
     *
     * 示例：domainSignMapper.getDomainSignList(projectId, "api")
     */
    List<DomainSign> getDomainSignList(String projectId, String condition);
}
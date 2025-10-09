package com.autotest.mapper;

import com.autotest.domain.Version;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：版本管理
 * 职责：按名称查询版本、保存/删除版本、按条件检索版本列表。
 */
@Mapper
public interface VersionMapper {

    /**
     * 根据名称查询版本
     * @param projectId 项目ID
     * @param name      版本名称
     * @return Version  版本实体
     */
    Version getVersionByName(String projectId, String name);

    /**
     * 保存版本（新增或更新）
     * @param version 版本实体
     */
    void saveVersion(Version version);

    /**
     * 删除版本
     * @param id 版本ID
     */
    void deleteVersion(String id);

    /**
     * 条件查询版本列表
     * @param projectId 项目ID
     * @param condition 关键字（支持模糊）
     * @return List<Version> 版本列表
     */
    List<Version> getVersionList(String projectId, String condition);
}
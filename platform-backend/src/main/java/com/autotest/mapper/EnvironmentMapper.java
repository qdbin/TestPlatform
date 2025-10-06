package com.autotest.mapper;

import com.autotest.domain.Environment;
import com.autotest.dto.EnvironmentDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：环境及参数管理
 * 职责：保存/删除环境、重名校验、获取全部环境与条件列表查询。
 */
@Mapper
public interface EnvironmentMapper {
    /**
     * 保存环境（新增或更新）
     * @param environment 环境实体
     */
    void saveEnvironment(Environment environment);

    /**
     * 删除环境
     * @param id 环境ID
     */
    void deleteEnvironment(String id);

    /**
     * 校验并获取重名环境
     * @param projectId 项目ID
     * @param name      环境名称
     * @return Environment 重名环境实体（不存在返回null）
     */
    Environment getEnvironmentByName(String projectId, String name);

    /**
     * 获取项目下全部环境列表
     * @param projectId 项目ID
     * @return List<Environment> 环境列表
     */
    List<Environment> getAllEnvironment(String projectId);

    /**
     * 条件查询环境列表（含统计或额外字段）
     * @param projectId 项目ID
     * @param condition 关键字（支持模糊）
     * @return List<EnvironmentDTO> 环境列表（DTO）
     */
    List<EnvironmentDTO> getEnvironmentList(String projectId, String condition);
}
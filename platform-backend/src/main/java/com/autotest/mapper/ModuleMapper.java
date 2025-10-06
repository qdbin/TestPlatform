package com.autotest.mapper;

import com.autotest.dto.ModuleDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：模块数据访问
 * 用途：保存、删除、按父名称查询与树列表构建
 */
@Mapper
public interface ModuleMapper {
    /**
     * 保存模块（新增或更新）
     *
     * @param module   // 模块DTO（含名称/父ID/项目ID等）
     * @return void    // 无返回
     *
     * 示例：
     *     入参：module.id为空表示新增
     *     调用：moduleMapper.saveModule(module)
     *     返回：无
     */
    void saveModule(ModuleDTO module);

    /**
     * 删除模块
     *
     * @param moduleType // 模块类型（表前缀）
     * @param id         // 模块ID
     * @return void      // 无返回
     */
    void deleteModule(String moduleType, String id);

    /**
     * 根据父ID与名称查询模块
     *
     * @param moduleType // 模块类型（表前缀）
     * @param name       // 模块名称
     * @param parentId   // 父模块ID
     * @param projectId  // 项目ID
     * @return ModuleDTO // 匹配到的模块DTO
     */
    ModuleDTO getModuleByParentAndName(String moduleType, String name, String parentId, String projectId);

    /**
     * 查询项目下模块列表
     *
     * @param moduleType     // 模块类型（表前缀）
     * @param projectId      // 项目ID
     * @return List<ModuleDTO> // 模块DTO列表
     *
     * 说明：用于构建树结构，返回包含label等扩展字段
     */
    List<ModuleDTO> getModuleList(String moduleType, String projectId);

    /**
     * 统计模块下数据量（用于删除前校验）
     *
     * @param moduleType // 模块类型（表前缀）
     * @param moduleId   // 模块ID
     * @return Integer   // 相关数据数量
     */
    Integer getModuleDataById(String moduleType, String moduleId);
}
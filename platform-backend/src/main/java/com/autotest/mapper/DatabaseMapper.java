package com.autotest.mapper;

import com.autotest.domain.Database;
import com.autotest.dto.DatabaseDTO;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

/**
 * 映射：数据库配置数据访问
 * 用途：保存、删除、按环境查询名称与列表
 */
@Mapper
public interface DatabaseMapper {
    /**
     * 保存数据库配置（新增或更新）
     *
     * @param domain     // 数据库实体/DTO
     * @return void      // 无返回
     */
    void saveDatabase(Database domain);

    /**
     * 删除数据库配置
     *
     * @param id        // 主键ID
     * @return void     // 无返回
     */
    void deleteDatabase(String id);

    /**
     * 通过环境与键查询数据库
     *
     * @param environmentId // 环境ID
     * @param databaseKey   // 数据库键
     * @return Database     // 数据库实体
     */
    Database getDatabaseByName(String environmentId, String databaseKey);

    /**
     * 查询项目下的数据库键名称列表
     *
     * @param projectId      // 项目ID
     * @return List<String>  // 键名称列表
     */
    List<String> getDatabaseNameList(String projectId);

    /**
     * 查询环境下数据库列表
     *
     * @param environmentId     // 环境ID
     * @return List<DatabaseDTO> // 数据库列表
     */
    List<DatabaseDTO> getDatabaseList(String environmentId);
}
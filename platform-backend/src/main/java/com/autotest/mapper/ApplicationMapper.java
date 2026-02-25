package com.autotest.mapper;

import com.autotest.domain.Application;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：应用配置数据访问
 * 用途：按名称/ID查询、保存、删除与列表查询
 */
@Mapper
public interface ApplicationMapper {
    /**
     * 根据名称查询应用
     *
     *     @param projectId // 项目ID
     *     @param name      // 应用名称
     *     @return Application // 应用实体
     */
    Application getApplicationByName(String projectId, String name);

    /**
     * 根据ID查询应用
     *
     *     @param id           // 应用ID
     *     @return Application // 应用实体
     */
    Application getApplicationById(String id);

    /**
     * 保存应用（新增或更新）
     *
     *     @param application // 应用实体
     *     @return void       // 无返回
     */
    void saveApplication(Application application);

    /**
     * 删除应用
     *
     *     @param id     // 应用ID
     *     @return void  // 无返回
     */
    void deleteApplication(String id);

    /**
     * 条件查询应用列表
     *
     *     @param projectId // 项目ID
     *     @param condition // 关键字（支持模糊）
     *     @param system    // 系统类型（如web/api/app）
     *     @return List<Application> // 应用列表
     */
    List<Application> getApplicationList(String projectId, String condition, String system);
}

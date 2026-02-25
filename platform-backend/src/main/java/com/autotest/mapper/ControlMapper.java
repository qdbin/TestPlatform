package com.autotest.mapper;

import com.autotest.domain.Control;
import com.autotest.dto.ControlDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：控件数据访问
 * 用途：新增/更新/删除控件，按模块查询与分页列表查询，以及详情查询
 */
@Mapper
public interface ControlMapper {
    /**
     * 新增控件
     * 
     *     @param control // 控件实体
     *     @return void   // 无返回
     */
    void addControl(Control control);

    /**
     * 更新控件
     * 
     *     @param control // 控件实体
     *     @return void   // 无返回
     */
    void updateControl(Control control);

    /**
     * 删除控件
     * 
     *     @param id    // 控件ID
     *     @return void // 无返回
     */
    void deleteControl(String id);

    /**
     * 查询模块下控件列表
     * 
     *     @param projectId // 项目ID
     *     @param moduleId  // 模块ID
     *     @param system    // 系统类型
     *     @return List<Control> // 控件列表
     */
    List<Control> getModuleControlList(String projectId, String moduleId, String system);

    /**
     * 分页查询控件列表
     * 
     *     @param request             // 查询请求（项目/模块/系统/条件）
     *     @return List<ControlDTO>   // 控件扩展DTO列表
     */
    List<ControlDTO> getControlList(QueryRequest request);

    /**
     * 根据ID查询控件详情
     * 
     *     @param id        // 控件ID
     *     @return ControlDTO // 控件扩展DTO
     */
    ControlDTO getControlById(String id);
}
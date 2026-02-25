package com.autotest.mapper;

import com.autotest.domain.Element;
import com.autotest.dto.ElementDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：页面元素数据访问
 * 用途：新增、更新、删除、按模块与条件查询
 */
@Mapper
public interface ElementMapper {
    /**
     * 新增元素
     *
     * @param element  // 元素实体
     * @return void    // 无返回
     */
    void addElement(Element element);

    /**
     * 更新元素
     *
     * @param element  // 元素实体
     * @return void    // 无返回
     */
    void updateElement(Element element);

    /**
     * 删除元素
     *
     * @param id       // 元素ID
     * @return void    // 无返回
     */
    void deleteElement(String id);

    /**
     * 查询模块下元素列表
     *
     * @param projectId // 项目ID
     * @param moduleId  // 模块ID
     * @return List<Element> // 元素列表
     */
    List<Element> getModuleElementList(String projectId, String moduleId);

    /**
     * 条件查询元素列表
     *
     * @param request    // 查询条件（分页/筛选）
     * @return List<ElementDTO> // 元素列表（DTO）
     */
    List<ElementDTO> getElementList(QueryRequest request);

    /**
     * 通过ID查询元素详情
     *
     * @param id        // 元素ID
     * @return ElementDTO // 元素详情（DTO）
     */
    ElementDTO getElementById(String id);
}
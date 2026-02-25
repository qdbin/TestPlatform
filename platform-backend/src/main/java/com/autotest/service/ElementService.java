package com.autotest.service;

import com.autotest.domain.Element;
import com.autotest.mapper.ElementMapper;
import com.autotest.dto.ElementDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;

/**
 * 服务：页面元素维护
 *     职责：新增/更新；删除；按模块与条件查询列表
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ElementService {

    @Resource
    private ElementMapper elementMapper;

    /**
     * 保存页面元素（新增或更新）
     *
     * @param element  // 元素实体
     * @return void    // 无返回
     */
    public void saveElement(Element element) {
        if(element.getId().equals("") || element.getId() == null){ // 新增元素
            element.setId(UUID.randomUUID().toString()); // 生成主键
            element.setCreateTime(System.currentTimeMillis()); // 创建时间
            element.setUpdateTime(System.currentTimeMillis()); // 更新时间
            element.setCreateUser(element.getUpdateUser()); // 创建人
            element.setStatus("Normal"); // 初始状态
            elementMapper.addElement(element); // 新增落库
        }else{ // 修改元素
            element.setUpdateTime(System.currentTimeMillis()); // 刷新时间
            elementMapper.updateElement(element); // 更新落库
        }
    }

    /**
     * 删除页面元素
     *
     * @param element  // 元素实体（含id）
     * @return void    // 无返回
     */
    public void deleteElement(Element element) {
        elementMapper.deleteElement(element.getId()); // 根据主键删除
    }

    /**
     * 查询模块下元素列表
     *
     * @param projectId   // 项目ID
     * @param moduleId    // 模块ID
     * @return List<Element> // 元素列表
     */
    public List<Element> getModuleElementList(String projectId, String moduleId) {
        return elementMapper.getModuleElementList(projectId, moduleId); // 委托mapper查询
    }

    /**
     * 条件查询元素列表
     *
     * @param request             // 查询条件（分页/筛选）
     * @return List<ElementDTO>   // 元素列表（DTO）
     */
    public List<ElementDTO> getElementList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%"); // 模糊匹配包装
        }
        return elementMapper.getElementList(request); // 委托mapper查询
    }

}

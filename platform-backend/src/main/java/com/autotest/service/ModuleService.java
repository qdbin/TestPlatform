package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.common.exception.LMException;
import com.autotest.mapper.ModuleMapper;
import com.autotest.dto.ModuleDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 服务：模块管理
 * 
 *     职责简述：提供模块的新增/更新、删除校验与树结构列表构建
 *     高频功能：
 *         1) 保存模块（含重名校验与时间字段维护）
 *         2) 删除模块（含数据占用校验）
 *         3) 构建项目下模块树（根节点+递归子节点）
 * 
 *     示例片段（入口与调用）：
 *         save(moduleDTO) -> moduleMapper.saveModule(moduleDTO)
 *         getModuleList(type, projectId) -> nodeList(all, rootId)
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ModuleService {

    @Resource
    private ModuleMapper moduleMapper;

    /**
     * 保存模块（新增或更新）
     * 
     *     功能：
     *         - 校验同父节点下重名
     *         - 新增时生成ID与时间戳；更新时刷新更新时间
     *         - 持久化并补充展示字段label
     * 
     *     @param module    // 模块DTO（含name/parentId/projectId等）
     *     @return ModuleDTO // 保存后的模块DTO（含label）
     * 
     *     入参示例：
     *         module = { id:null, name:"页面", parentId:"0", projectId:"p1" }
     *     调用示例：
     *         result = moduleService.save(module)
     *     返回示例：
     *         result = { id:"UUID", name:"页面", label:"页面", ... }
     */
    public ModuleDTO save(ModuleDTO module) {
        ModuleDTO oldModule = moduleMapper.getModuleByParentAndName(module.getModuleType(),
                module.getName(), module.getParentId(), module.getProjectId());
        if(oldModule != null){
            // 关键步骤：同父节点下重名校验
            throw new DuplicateException("当前父模块下已有重名模块");
        }
        if(module.getId() == null){
            // 新增路径：生成主键与时间戳
            module.setId(UUID.randomUUID().toString());
            module.setCreateTime(System.currentTimeMillis());
            module.setUpdateTime(System.currentTimeMillis());
            module.setCreateUser(module.getUpdateUser()); // 记录创建人
        }else{
            // 更新路径：刷新更新时间
            module.setUpdateTime(System.currentTimeMillis());
        }
        moduleMapper.saveModule(module); // 持久化保存
        module.setLabel(module.getName()); // 展示标签赋值
        return module;
    }

    /**
     * 删除模块
     * 
     *     功能：删除前校验模块关联数据量，存在数据则拒绝删除
     * 
     *     @param module   // 模块DTO（含id/moduleType）
     *     @return void    // 无返回
     */
    public void delete(ModuleDTO module) {
        Integer count = moduleMapper.getModuleDataById(module.getModuleType(), module.getId());
        if(count>0){
            // 关键步骤：存在数据占用，阻止删除
            throw new LMException("当前模块下已有相关数据，无法删除！");
        }
        moduleMapper.deleteModule(module.getModuleType(), module.getId()); // 执行删除
    }

    /**
     * 获取模块树列表
     * 
     *     功能：查询项目下所有模块，构建根到叶子的树结构
     * 
     *     @param moduleType       // 模块类型
     *     @param projectId        // 项目ID
     *     @return List<ModuleDTO> // 树结构的根节点列表
     */
    public List<ModuleDTO> getModuleList(String moduleType, String projectId){
        List<ModuleDTO> fina = new ArrayList<>();
        List<ModuleDTO> apiModuleDTOS = moduleMapper.getModuleList(moduleType, projectId); // 查询全部模块
        for(ModuleDTO apiModuleDTO: apiModuleDTOS){
            // 若是根节点（ParentId==0）
            if(apiModuleDTO.getParentId().equals("0")){
                // 根节点：递归填充子节点
                apiModuleDTO.setChildren(this.nodeList(apiModuleDTOS, apiModuleDTO.getId()));
                fina.add(apiModuleDTO); // 收集根节点
            }
        }
        return fina;
    }

    /**
     * 递归构建子节点列表
     * 
     *     功能：按parentId查找并填充所有直接/间接子节点
     * 
     *     @param apiModules       // 全量模块列表
     *     @param parentId         // 父节点ID
     *     @return List<ModuleDTO> // 子节点列表
     */
    public List<ModuleDTO> nodeList(List<ModuleDTO> apiModules, String parentId){
        // 递归查找所有的子节点
        List<ModuleDTO> childrenList = new ArrayList<>();
        // 遍历每个结点
        for(ModuleDTO apiModuleDTO: apiModules){
            // 若是parentId==父节点id，则放到childrenList
            if(apiModuleDTO.getParentId().equals(parentId)){
                // 继续递归
                apiModuleDTO.setChildren(this.nodeList(apiModules, apiModuleDTO.getId())); // 递归填充
                childrenList.add(apiModuleDTO); // 收集匹配项
            }
        }
        return childrenList;
    }

}

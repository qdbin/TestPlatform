package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Environment;
import com.autotest.mapper.EnvironmentMapper;
import com.autotest.dto.EnvironmentDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：环境管理（EnvironmentService）
 *     主要职责：环境新增/更新、删除、查询列表
 *     高频功能：去重校验、保存环境、按项目查询
 *
 * 示例（调用示例片段）：
 *     // 入口：Controller 调用
 *     // saveEnvironment(env);
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class EnvironmentService {

    @Resource
    private EnvironmentMapper environmentMapper;

    /**
     * 保存环境（新增或更新）
     *
     * @param environment    // 环境实体，包含名称、项目ID等
     *
     * 说明：根据是否存在ID判断新增或更新；对同名环境进行去重校验
     */
    public void saveEnvironment(Environment environment) {
        Environment oldEnvironment = environmentMapper.getEnvironmentByName(environment.getProjectId(), environment.getName());
        if(oldEnvironment != null && !Objects.equals(oldEnvironment.getId(), environment.getId())){
            throw new DuplicateException("当前项目已有重名环境");
        }
        if(environment.getId() == null || environment.getId().equals("")){
            //新增环境
            environment.setId(UUID.randomUUID().toString());
            environment.setCreateTime(System.currentTimeMillis()); // 记录创建时间
            environment.setUpdateTime(System.currentTimeMillis()); // 初始化更新时间
            environment.setCreateUser(environment.getUpdateUser()); // 设置创建人
        }else{
            // 更新环境
            environment.setUpdateTime(System.currentTimeMillis()); // 刷新更新时间
        }
        environmentMapper.saveEnvironment(environment); // 持久化环境数据
    }

    /**
     * 删除环境
     *
     * @param environment    // 环境实体，仅需携带ID
     *
     */
    public void deleteEnvironment(Environment environment) {
        environmentMapper.deleteEnvironment(environment.getId()); // 根据ID删除
    }

    /**
     * 查询项目下所有环境（简要信息）
     *
     * @param projectId      // 项目ID
     * @return List<Environment> // 环境列表
     */
    public List<Environment> getAllEnvironment(String projectId){
        return environmentMapper.getAllEnvironment(projectId);
    }

    /**
     * 查询环境列表（含筛选条件）
     *
     * @param projectId      // 项目ID
     * @param condition      // 名称匹配条件（模糊）
     * @return List<EnvironmentDTO> // 环境DTO列表
     */
    public List<EnvironmentDTO> getEnvironmentList(String projectId, String condition){
        if(condition != null && !condition.equals("")){
            condition = ("%"+condition+"%"); // 构造模糊匹配条件
        }
        return environmentMapper.getEnvironmentList(projectId, condition);
    }


}

package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.ParamData;
import com.autotest.domain.ParamGroup;
import com.autotest.mapper.CommonParamMapper;
import com.autotest.dto.ParamDataDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：公共参数管理
 * 职责：公共参数与分组的增删改查，提供分组与项目维度的查询能力。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class CommonParamService {

    @Resource
    private CommonParamMapper commonParamMapper;

    /**
     * 保存参数数据（新增或更新），重名校验并维护审计字段
     *
     * @param paramData // 参数数据实体
     * @return void     // 无返回；重名抛出 DuplicateException
     */
    public void saveParamData(ParamData paramData) {
        // 判断DB中是否已有ParamData(通过组id,组数据名)
        ParamData oldParam = commonParamMapper.getParamByGroupAndName(paramData.getGroupId(), paramData.getName());
        // DB存在&&相等（更新，前端必须传入id,前端不传统一当作新增）
        if(oldParam != null && !Objects.equals(oldParam.getId(), paramData.getId())){
            throw new DuplicateException("当前项目已有重名参数");
        }

        // 参数数据为空，即DB中没有
        if(paramData.getId() == null || paramData.getId().equals("")){
            //新增参数
            paramData.setId(UUID.randomUUID().toString());
            paramData.setCreateTime(System.currentTimeMillis());
            paramData.setUpdateTime(System.currentTimeMillis());
            paramData.setCreateUser(paramData.getUpdateUser());
        }else{
            // 更新参数
            paramData.setUpdateTime(System.currentTimeMillis());
        }
        commonParamMapper.saveParamData(paramData);
    }

    /**
     * 删除参数数据
     *
     * @param paramData // 参数数据实体（至少包含id）
     * @return void     // 无返回
     */
    public void deleteParamData(ParamData paramData) {
        commonParamMapper.deleteParamData(paramData.getId());
    }

    /**
     * 分页查询分组下参数数据（包装模糊条件）
     *
     * @param groupId   // 分组ID
     * @param condition // 模糊条件（名称）
     * @return List<ParamDataDTO> // 参数数据列表
     */
    public List<ParamDataDTO> getParamDataList(String groupId, String condition){
        if(condition != null && !condition.equals("")){
            condition = ("%"+condition+"%");
        }
        return commonParamMapper.getParamDataList(groupId, condition);
    }

    /**
     * 按分组名称与项目查询参数数据
     *
     * @param groupName // 分组名称
     * @param projectId // 项目ID
     * @return List<ParamDataDTO> // 参数数据列表
     */
    public List<ParamDataDTO> getParamDataListByGroupName(String groupName, String projectId){
        return commonParamMapper.getParamDataListByGroupName(groupName, projectId);
    }

    /**
     * 查询项目下的自定义参数列表
     *
     * @param projectId // 项目ID
     * @return List<ParamData> // 自定义参数列表
     */
    public List<ParamData> getCustomParamList(String projectId){
        return commonParamMapper.getCustomParamList(projectId);
    }

    /**
     * 查询项目下的参数分组列表
     *
     * @param projectId // 项目ID
     * @return List<ParamGroup> // 参数分组列表
     */
    public List<ParamGroup> getParamGroupList(String projectId){
        return commonParamMapper.getParamGroupList(projectId);
    }

}

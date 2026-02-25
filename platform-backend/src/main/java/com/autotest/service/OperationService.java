package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.OperationType;
import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Operation;
import com.autotest.mapper.OperationMapper;
import com.autotest.dto.OperationDTO;
import com.autotest.dto.OperationGroupDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * 服务：操作管理
 * 
 *     职责：提供操作的新增/更新、删除、详情、分组查询与分页列表。
 *     关键点：
 *         - 元素/数据字段为 JSON 字符串，入库前统一解析/规范化
 *         - 新增时进行重名校验（项目/UI类型/系统维度）
 *         - 删除为软删除（状态位），查询均过滤状态
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class OperationService {

    @Resource
    private OperationMapper operationMapper;

    /**
     * 保存操作（新增或更新）
     * @param operation // 操作实体（含元素/数据/代码等）
     * @return void     // 无返回
     */
    public void saveOperation(Operation operation){
        // 解析并规范化元素字段（保持为 JSON 字符串）
        if(operation.getElement() != null){
            JSONArray element = JSONArray.parseArray(operation.getElement());
            operation.setElement(element.toJSONString());
        }
        // 解析并规范化数据字段（保持为 JSON 字符串）
        if(operation.getData() != null){
            JSONArray data = JSONArray.parseArray(operation.getData());
            operation.setData(data.toJSONString());
        }
        // 分支：新增 vs 更新（按ID是否为空）
        if(operation.getId().equals("") || operation.getId() == null){ // 新增操作
            // 重名校验（项目/UI类型/系统 维度唯一）
            Operation oldOperation = operationMapper.getOperationByName(operation.getName(), operation.getProjectId(), operation.getUiType(), operation.getSystem());
            if(oldOperation != null){
                throw new DuplicateException("操作名称重复");
            }
            // 初始化主键与审计字段
            operation.setId(UUID.randomUUID().toString());
            operation.setCreateTime(System.currentTimeMillis());
            operation.setUpdateTime(System.currentTimeMillis());
            operation.setCreateUser(operation.getUpdateUser());
            operationMapper.addOperation(operation);
        }else{ // 修改操作
            // 更新审计字段
            operation.setUpdateTime(System.currentTimeMillis());
            operationMapper.updateOperation(operation);
        }
    }

    /**
     * 删除操作（软删除）
     * @param id     // 操作ID
     * @param uiType // UI类型（web/app）
     * @return void  // 无返回
     */
    public void deleteOperation(String id, String uiType) {
        operationMapper.deleteOperation(id, uiType);
    }

    /**
     * 获取操作详情
     * @param operationId // 操作ID
     * @param uiType      // UI类型
     * @return Operation  // 操作实体详情
     */
    public Operation getOperationDetail(String operationId, String uiType) {
        return operationMapper.getOperationDetail(operationId, uiType);
    }

    /**
     * 获取分组操作列表
     * @param uiType    // UI类型（web/app）
     * @param system    // 系统标识（app）
     * @param projectId // 项目ID
     * @return List<OperationGroupDTO> // 操作分组列表
     */
    public List<OperationGroupDTO> getGroupOperationList(String uiType, String system, String projectId) {
        List<OperationGroupDTO> operationGroupDTOList = new ArrayList<>();
        List<String> operationTypeList = OperationType.enumList(uiType);
        for(String operationType:operationTypeList){
            OperationGroupDTO operationGroup = new OperationGroupDTO();
            operationGroup.setId(operationType);
            operationGroup.setName(OperationType.valueOf(operationType.toUpperCase(Locale.ROOT)).toLabel());
            List<OperationDTO> operationList = operationMapper.getGroupOperationList(projectId, uiType, system, operationType);
            for (OperationDTO operation:operationList){
                // 解析元素/数据列表，填充默认值以便前端使用
                JSONArray elements = (JSONArray) JSONArray.parse(operation.getElement());
                for(int i=0; i< elements.size(); i++){
                    JSONObject element = elements.getJSONObject(i);
                    element.put("custom", false);
                    element.put("moduleId", "");
                    element.put("moduleName", "");
                    element.put("id", "");
                    element.put("name", "");
                    element.put("by", "");
                    element.put("expression", "");
                    element.put("selectElements", new JSONArray());
                }
                operation.setElementList(elements);
                operation.setDataList((JSONArray) JSONArray.parse(operation.getData()));
            }
            operationGroup.setOperationList(operationList);
            operationGroupDTOList.add(operationGroup);
        }
        return operationGroupDTOList;
    }

    /**
     * 分页查询操作列表
     * @param request // 查询条件（项目ID/类型/系统/模糊条件等）
     * @return List<OperationDTO> // 操作列表（含创建人）
     */
    public List<OperationDTO> getOperationList(QueryRequest request) {
        // 处理模糊条件（like 查询）
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return operationMapper.getOperationList(request);
    }

}

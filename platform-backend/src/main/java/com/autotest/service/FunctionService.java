package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Function;
import com.autotest.mapper.FunctionMapper;
import com.autotest.dto.FunctionDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;

/**
 * 服务：函数管理
 * 职责：提供函数的保存、删除、详情与列表查询，包含参数规范化与重名校验等关键逻辑。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class FunctionService {

    @Resource
    private FunctionMapper functionMapper;

    /**
     * 保存函数（新增或更新）
     *
     * 关键点：
     * - 入参字段 `param` 进行 JSON 数组规范化存储
     * - 新增时按项目维度校验函数名称唯一性
     * - 维护审计字段（创建/更新时间、创建人）
     *
     * @param function // 函数实体
     * @return void    // 无返回
     */
    public void saveFunction(Function function){
        // 函数参数非空,确保传入的是JSON数组格式
        if(function.getParam() != null){
            JSONArray params = JSONArray.parseArray(function.getParam());
            function.setParam(params.toJSONString());
        }
        // 如果id为空则为新增，id非空则为更新
        if(function.getId().equals("") || function.getId() == null){ // 新增函数
            Function oldFunction = functionMapper.getFunctionByName(function.getProjectId(), function.getName());
            if (oldFunction != null){
                throw new DuplicateException("函数名称重复");
            }
            function.setId(UUID.randomUUID().toString());
            function.setCreateTime(System.currentTimeMillis());
            function.setUpdateTime(System.currentTimeMillis());
            function.setCreateUser(function.getUpdateUser());
            functionMapper.addFunction(function);
        }else{ // 修改函数
            function.setUpdateTime(System.currentTimeMillis());
            functionMapper.updateFunction(function);
        }
    }

    /**
     * 删除函数（逻辑删除）
     *
     * @param id   // 函数ID
     * @return void // 无返回
     */
    public void deleteFunction(String id) {
        functionMapper.deleteFunction(id);
    }

    /**
     * 获取函数详情
     *
     * @param functionId // 函数ID
     * @return Function  // 详情实体
     */
    public Function getFunctionDetail(String functionId) {
        return functionMapper.getFunctionDetail(functionId);
    }
    /**
     * 查询项目下自定义函数列表
     *
     * @param projectId         // 项目ID
     * @return List<Function>   // 自定义函数列表
     */
    public List<Function> getCustomFunctionList(String projectId) {
        return functionMapper.getCustomFunctionList(projectId);
    }

    /**
     * 分页查询函数列表（含创建人用户名）
     *
     * 关键点：
     * - 对条件进行模糊化包装（like '%condition%')
     * - 返回扩展DTO以承载用户名等展示字段
     *
     * @param request // 查询请求（含项目ID、条件等）
     * @return List<FunctionDTO> // 扩展DTO列表
     */
    public List<FunctionDTO> getFunctionList(QueryRequest request) {
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return functionMapper.getFunctionList(request.getProjectId(), request.getCondition());
    }

}

package com.autotest.service;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.autotest.domain.Api;
import com.autotest.mapper.ApiMapper;
import com.autotest.dto.ApiDTO;
import com.autotest.request.ApiRequest;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;

/**
 * 服务：接口定义维护
 *     职责：新增/更新；删除；详情与列表查询
 *     示例：入口 saveApi/deleteApi/getApiDetail/getApiList 调用持久化层
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ApiService {
    @Resource
    private ApiMapper apiMapper;

    /**
     * 保存接口定义（新增或更新）
     *
     * @param apiRequest   // 接口请求载体（含入参）
     * @return String      // 接口ID
     *
     * 示例：
     *     入参示例：apiRequest.id为空为新增
     *     调用示例：apiService.saveApi(apiRequest)
     *     返回示例：生成或现有的api.id
     */
    public String saveApi(ApiRequest apiRequest) {
        JSONObject apiObject = (JSONObject) JSON.toJSON(apiRequest);
        Api api = apiObject.toJavaObject(Api.class);

        // 新增接口
        if(api.getId().equals("") || api.getId() == null){
            // 初始化主键与时间戳
            api.setId(UUID.randomUUID().toString()); // 生成主键
            api.setCreateTime(System.currentTimeMillis()); // 创建时间
            api.setUpdateTime(System.currentTimeMillis()); // 更新时间
            api.setCreateUser(api.getUpdateUser()); // 记录创建人
            api.setStatus("Normal"); // 初始状态
            apiMapper.addApi(api); // 新增落库
        }
        // 修改接口
        else{
            api.setUpdateTime(System.currentTimeMillis()); // 刷新时间
            apiMapper.updateApi(api); // 更新落库
        }
        return api.getId();
    }

    /**
     * 删除接口定义
     *
     * @param apiRequest   // 请求载体（包含id）
     * @return void        // 无返回
     */
    public void deleteApi(ApiRequest apiRequest) {
        apiMapper.deleteApi(apiRequest.getId()); // 根据主键删除
    }

    /**
     * 获取接口详情
     *
     * @param apiId    // 接口主键ID
     * @return ApiDTO  // 接口详情（DTO）
     */
    public ApiDTO getApiDetail(String apiId) {
        return apiMapper.getApiDetail(apiId); // 查询详情
    }

    /**
     * 获取接口列表
     *
     * @param request               // 查询条件（分页/筛选）
     * @return List<ApiDTO>         // 列表数据
     */
    public List<ApiDTO> getApiList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%"); // 模糊匹配包装
        }
        return apiMapper.getApiList(request); // 查询列表
    }

}

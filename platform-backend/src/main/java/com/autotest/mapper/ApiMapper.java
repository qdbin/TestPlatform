package com.autotest.mapper;

import com.autotest.domain.Api;
import com.autotest.dto.ApiDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：接口定义数据访问（CRUD:Api）
 * 用途：持久化接口定义与查询列表
 */
@Mapper
public interface ApiMapper {
    /**
     * 新增接口定义
     *
     * @param api      // 接口实体数据
     * @return void    // 无返回
     */
    void addApi(Api api);

    /**
     * 更新接口定义
     *
     * @param api      // 接口实体数据
     * @return void    // 无返回
     */
    void updateApi(Api api);

    /**
     * 删除接口定义
     *
     * @param id       // 主键ID
     * @return void    // 无返回
     */
    void deleteApi(String id);

    /**
     * 获取接口详情
     *
     * @param id       // 主键ID
     * @return ApiDTO  // 接口详情（扩展字段）
     */
    ApiDTO getApiDetail(String id);

    /**
     * 获取接口列表
     *
     * @param request          // 查询请求（分页/条件）
     * @return List<ApiDTO>    // 接口列表
     */
    List<ApiDTO> getApiList(QueryRequest request);
}
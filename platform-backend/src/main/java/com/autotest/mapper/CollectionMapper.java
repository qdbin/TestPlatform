package com.autotest.mapper;

import com.autotest.domain.Collection;
import com.autotest.dto.CollectionDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：集合数据访问
 * 用途：集合的新增、更新、删除、详情与分页列表查询
 */
@Mapper
public interface CollectionMapper {
    /**
     * 新增集合
     *
     *     @param collection // 集合实体（名称/设备/版本/项目ID等）
     *     @return void      // 无返回
     *
     *     示例：
     *         入参：collection.id为空表示新增
     *         调用：collectionMapper.addCollection(collection)
     *         返回：无
     */
    void addCollection(Collection collection);

    /**
     * 更新集合
     *
     *     @param collection // 集合实体（根据id更新名称、版本、描述等）
     *     @return void      // 无返回
     */
    void updateCollection(Collection collection);

    /**
     * 删除集合（逻辑删除）
     *
     *     @param id   // 集合ID
     *     @return void // 无返回
     */
    void deleteCollection(String id);

    /**
     * 查询集合详情
     *
     *     @param id           // 集合ID
     *     @return CollectionDTO // 集合扩展DTO（含版本名称等）
     */
    CollectionDTO getCollectionDetail(String id);

    /**
     * 分页查询集合列表
     *
     *     @param request             // 查询请求（项目ID+模糊条件）
     *     @return List<CollectionDTO> // 集合扩展DTO列表（含用户名/版本名）
     */
    List<CollectionDTO> getCollectionList(QueryRequest request);
}
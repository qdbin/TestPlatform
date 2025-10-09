package com.autotest.mapper;

import com.autotest.domain.CollectionCase;
import com.autotest.dto.CollectionCaseDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * MyBatis Mapper：集合-用例关系
 * 负责集合下用例的新增、删除、查询统计等数据库操作
 */
@Mapper
public interface CollectionCaseMapper {
    /**
     * 批量新增集合用例关系
     * @param collectionCases 集合-用例关系列表
     */
    void addCollectionCase(List<CollectionCase> collectionCases);

    /**
     * 删除指定集合下的所有用例关系
     * @param collectionId 集合ID
     */
    void deleteCollectionCase(String collectionId);

    /**
     * 查询集合下的用例明细列表
     * @param collectionId 集合ID
     * @return 用例明细列表
     */
    List<CollectionCaseDTO> getCollectionCaseList(String collectionId);

    /**
     * 统计集合下的用例数量
     * @param collectionId 集合ID
     * @return 用例总数
     */
    Integer getCollectionCaseCount(String collectionId);

    /**
     * 查询集合下用例的类型集合
     * @param collectionId 集合ID
     * @return 用例类型列表，如 Api/Web/App
     */
    List<String> getCollectionCaseTypes(String collectionId);
}
package com.autotest.mapper;

import com.autotest.domain.AiApiIndex;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * Mapper：AI接口索引数据访问
 */
@Mapper
public interface AiApiIndexMapper {
    
    void addApiIndex(AiApiIndex apiIndex);
    
    void updateApiIndex(AiApiIndex apiIndex);
    
    void deleteApiIndex(@Param("id") String id);
    
    void deleteApiIndexByProject(@Param("projectId") String projectId);
    
    AiApiIndex getApiIndexById(@Param("id") String id);
    
    List<AiApiIndex> getApiIndexList(@Param("projectId") String projectId);
    
    List<AiApiIndex> getApiIndexByStatus(@Param("projectId") String projectId, @Param("indexedStatus") String indexedStatus);
    
    AiApiIndex getApiIndexByApiId(@Param("projectId") String projectId, @Param("apiId") String apiId);
}

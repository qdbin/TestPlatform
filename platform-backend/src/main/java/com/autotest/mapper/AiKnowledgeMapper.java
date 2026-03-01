package com.autotest.mapper;

import com.autotest.domain.AiKnowledge;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * Mapper：AI知识库数据访问
 */
@Mapper
public interface AiKnowledgeMapper {
    
    void addKnowledge(AiKnowledge knowledge);
    
    void updateKnowledge(AiKnowledge knowledge);
    
    void deleteKnowledge(@Param("id") String id);
    
    AiKnowledge getKnowledgeById(@Param("id") String id);
    
    List<AiKnowledge> getKnowledgeList(@Param("projectId") String projectId);
    
    List<AiKnowledge> getKnowledgeListByType(@Param("projectId") String projectId, @Param("docType") String docType);
}

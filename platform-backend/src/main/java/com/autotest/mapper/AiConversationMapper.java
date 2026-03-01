package com.autotest.mapper;

import com.autotest.domain.AiConversation;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * Mapper：AI会话历史数据访问
 */
@Mapper
public interface AiConversationMapper {
    
    void addConversation(AiConversation conversation);
    
    void updateConversation(AiConversation conversation);
    
    void deleteConversation(@Param("id") String id);
    
    AiConversation getConversationById(@Param("id") String id);
    
    List<AiConversation> getConversationList(@Param("projectId") String projectId, @Param("userId") String userId);
    
    List<AiConversation> getConversationListByType(@Param("projectId") String projectId, @Param("userId") String userId, @Param("sessionType") String sessionType);
}

package com.autotest.mapper;

import com.autotest.domain.AiConfig;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * Mapper：AI配置数据访问
 */
@Mapper
public interface AiConfigMapper {
    
    void addConfig(AiConfig config);
    
    void updateConfig(AiConfig config);
    
    void deleteConfig(@Param("id") String id);
    
    AiConfig getConfigById(@Param("id") String id);
    
    List<AiConfig> getConfigList(@Param("projectId") String projectId);
    
    List<AiConfig> getGlobalConfig();
    
    AiConfig getConfigByKey(@Param("configKey") String configKey, @Param("projectId") String projectId);
}

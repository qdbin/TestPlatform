package com.autotest.domain;

import lombok.Data;
import java.io.Serializable;

/**
 * 实体：AI配置
 * 用途：存储AI服务配置信息（API Key、模型等）
 */
@Data
public class AiConfig implements Serializable {
    private String id;
    private String configKey;
    private String configValue;
    private Integer isGlobal;
    private String projectId;
    private String status;
    private Long createTime;
    private Long updateTime;
}

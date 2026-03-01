package com.autotest.domain;

import lombok.Data;
import java.io.Serializable;

/**
 * 实体：AI接口索引
 * 用途：记录项目中哪些接口已同步到知识库
 */
@Data
public class AiApiIndex implements Serializable {
    private String id;
    private String projectId;
    private String apiId;
    private String apiName;
    private String apiPath;
    private String apiMethod;
    private String apiInfo;
    private String indexedStatus;
    private String errorMsg;
    private Long createTime;
    private Long updateTime;
}

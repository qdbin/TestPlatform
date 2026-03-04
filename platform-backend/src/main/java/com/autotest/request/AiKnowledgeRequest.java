package com.autotest.request;

import lombok.Data;

/**
 * Request：AI知识库请求
 */
@Data
public class AiKnowledgeRequest {
    private String id;
    private String projectId;
    private String parentId;
    private String name;
    private String content;
    private String docType;
    private String sourceType;
    private String updateUser;
}

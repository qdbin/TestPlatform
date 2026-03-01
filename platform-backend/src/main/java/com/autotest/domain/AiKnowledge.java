package com.autotest.domain;

import lombok.Data;
import java.io.Serializable;

/**
 * 实体：AI知识库文档
 * 用途：存储知识库文档内容，用于RAG检索
 */
@Data
public class AiKnowledge implements Serializable {
    private String id;
    private String projectId;
    private String name;
    private String content;
    private String docType;
    private String sourceType;
    private String status;
    private Long createTime;
    private Long updateTime;
    private String createUser;
    private String updateUser;
}

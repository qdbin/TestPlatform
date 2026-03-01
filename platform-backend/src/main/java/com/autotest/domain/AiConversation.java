package com.autotest.domain;

import lombok.Data;
import java.io.Serializable;

/**
 * 实体：AI会话历史
 * 用途：存储用户与AI的对话历史
 */
@Data
public class AiConversation implements Serializable {
    private String id;
    private String projectId;
    private String userId;
    private String sessionType;
    private String title;
    private String messages;
    private String context;
    private Integer useRag;
    private String status;
    private Long createTime;
    private Long updateTime;
}

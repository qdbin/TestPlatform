package com.autotest.dto;

import lombok.Data;

/**
 * DTO：AI对话请求
 */
@Data
public class AiChatRequest {
    private String projectId;
    private String message;
    private Boolean useRag;
    private String conversationId;
}

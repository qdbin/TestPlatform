package com.autotest.request;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class AiChatStreamRequest {
    private String projectId;
    private String message;
    private Boolean useRag;
    private List<Map<String, Object>> messages;
}

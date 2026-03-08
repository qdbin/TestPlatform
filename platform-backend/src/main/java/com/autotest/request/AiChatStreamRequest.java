package com.autotest.request;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class AiChatStreamRequest {
    /** 项目ID（必填） */
    private String projectId;
    /** 当前用户问题（必填） */
    private String message;
    /** 是否启用知识库检索，null按true处理 */
    private Boolean useRag;
    /**
     * 历史消息（可选）
     * 示例：[{"role":"user","content":"上个问题"},{"role":"assistant","content":"上个回答"}]
     */
    private List<Map<String, Object>> messages;
}

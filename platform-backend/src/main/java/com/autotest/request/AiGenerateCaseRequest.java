package com.autotest.request;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class AiGenerateCaseRequest {
    private String projectId;
    private String userRequirement;
    private List<String> selectedApis;
    private List<Map<String, Object>> messages;
}

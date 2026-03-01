package com.autotest.dto;

import lombok.Data;
import java.util.List;
import java.util.Map;

/**
 * DTO：AI用例生成请求
 */
@Data
public class AiGenerateCaseRequest {
    private String projectId;
    private String userRequirement;
    private List<String> selectedApis;
}

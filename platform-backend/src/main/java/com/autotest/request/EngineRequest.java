package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：引擎回传请求（文件/结果）
 * 用途：承载引擎上传文件或用例结果的凭据与数据
 */
@Setter
@Getter
public class EngineRequest {
    private String engineCode;                    // 引擎编码

    private String engineSecret;                  // 引擎密钥

    private String timestamp;                     // 时间戳

    private String taskId;                        // 任务ID

    private String fileName;                      // 文件名

    private String base64String;                  // Base64文件内容

    private List<CaseResultRequest> caseResultList; // 用例结果列表
}

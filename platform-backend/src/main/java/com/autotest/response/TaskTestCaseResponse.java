package com.autotest.response;

import lombok.Getter;
import lombok.Setter;

/**
 * 响应：任务中的用例条目
 * 用途：描述测试集合中的单个用例及其类型与顺序
 */
@Setter
@Getter
public class TaskTestCaseResponse {
    private Long index;   // 用例在集合中的顺序（从1开始）

    private String caseId;   // 用例ID

    private String caseType; // 用例类型（API/WEB/APP）

}

package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: DebugData
 * 职责: 存储调试用的临时数据内容
 */
@Data
public class DebugData implements Serializable {
    private String id;    // 主键ID

    private String data;  // 调试数据内容(JSON/文本)

}
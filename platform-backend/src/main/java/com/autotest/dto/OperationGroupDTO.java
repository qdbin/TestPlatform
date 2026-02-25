package com.autotest.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * DTO：操作分组视图
 * 用途：承载分组信息及其下操作列表，用于客户端展示。
 */
@Getter
@Setter
public class OperationGroupDTO {
    private String id;    // 分组ID

    private String name;  // 分组名称

    private List<OperationDTO> operationList; // 分组下的操作列表
}

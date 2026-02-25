package com.autotest.dto;

import com.alibaba.fastjson.JSONArray;
import com.autotest.domain.Operation;
import lombok.Getter;
import lombok.Setter;


/**
 * DTO：操作扩展视图
 * 用途：在基础 Operation 上追加展示/解析字段，
 *      包括创建人名称与已解析的元素/数据列表。
 */
@Getter
@Setter
public class OperationDTO extends Operation {

    private String username;     // 创建人用户名（展示用）

    private JSONArray dataList;  // 数据列表（由 data 解析）

    private JSONArray elementList; // 元素列表（由 element 解析）
}

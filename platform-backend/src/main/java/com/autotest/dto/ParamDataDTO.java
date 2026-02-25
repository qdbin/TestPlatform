package com.autotest.dto;

import com.autotest.domain.ParamData;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：公共参数数据扩展视图（继承 ParamData）
 * 用途：用于列表/详情展示时补充操作者用户名
 */
@Getter
@Setter
public class ParamDataDTO extends ParamData {

    /** 用户名称（创建/更新操作者的展示名） */
    private String username;

}

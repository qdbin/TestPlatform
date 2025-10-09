package com.autotest.request;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

/**
 * 请求：事务执行明细上报
 * 用途：记录单个事务的内容、日志、时长、状态与截图
 */
@Setter
@Getter
public class TransResultRequest {
    private String id;                     // 事务ID

    private String name;                   // 事务名称

    private String content;                // 执行内容（步骤/脚本）

    private String description;            // 描述信息

    private String log;                    // 执行日志

    private Integer during;                // 耗时（ms）

    private Integer status;                // 状态码（通过/失败/错误）

    private List<String> screenShotList;   // 截图列表（URL或Base64标识）

}

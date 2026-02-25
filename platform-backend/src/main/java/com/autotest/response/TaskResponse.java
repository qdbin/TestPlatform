package com.autotest.response;

import com.alibaba.fastjson.JSONObject;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：任务响应载体（taskId:status）
 * 用途：执行任务的配置、下载地址与结果数据
 */
@Setter
@Getter
public class TaskResponse {

    private String taskId;      // 任务ID

    private String taskType;    // 任务类型（plan/case/debug等）

    private String downloadUrl; // 数据包下载地址

    private Integer maxThread; // 最大并发数

    private Boolean reRun; // 是否失败重试

    private List<TaskTestCollectionResponse> testCollectionList;    // 非调试执行（集合列表）

    private JSONObject debugData; // 调试执行的用例数据

}

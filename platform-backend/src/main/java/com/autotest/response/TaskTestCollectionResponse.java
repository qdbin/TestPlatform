package com.autotest.response;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
    * 响应：任务测试集合载体
    * 用途：承载设备与集合下的用例列表
    */
@Setter
@Getter
public class TaskTestCollectionResponse {

    private String collectionId;                 // 集合ID

    private String deviceId;                     // 设备ID

    private List<TaskTestCaseResponse> testCaseList; // 集合下的用例列表

}

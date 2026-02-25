package com.autotest.request;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 请求：单个用例的执行结果上报
 * 用途：记录用例执行的时间范围、状态、次数及事务明细
 */
@Setter
@Getter
public class CaseResultRequest {
    private Integer status;         // 用例执行结果（0，1，2，3）（success,fail,error,skip）

    private Long startTime;         // 开始时间

    private Long endTime;           // 结束时间

    private String collectionId;    // collection_id

    private String caseId;          // case_id

    private String caseType;        // case_type

    private String caseName;        // case_name

    private String caseDesc;        // case_desc

    private Integer index;          // case_index

    private Integer runTimes;       // 执行次数

    private List<TransResultRequest> transactionList;   // case_api_result_list
}

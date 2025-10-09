package com.autotest.domain;

import lombok.Data;

import java.io.Serializable;

/**
 * 类: CollectionCase
 * 职责: 记录集合内用例的顺序与关联关系
 */
@Data
public class CollectionCase implements Serializable {
    private String id;           // 主键ID

    private Long index;          // 用例在集合中的执行顺序

    private String collectionId; // 所属集合ID

    private String caseId;       // 关联的用例ID

}
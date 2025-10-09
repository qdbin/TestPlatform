package com.autotest.dto;

import com.autotest.domain.Collection;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * 实体：集合扩展DTO
 * 用途：承载集合展示附加字段与用例列表
 */
@Getter
@Setter
public class CollectionDTO extends Collection {
    private String username;                  // 创建人用户名

    private String versionName;               // 版本名称

    private List<CollectionCaseDTO> collectionCases; // 集合下的用例列表

}

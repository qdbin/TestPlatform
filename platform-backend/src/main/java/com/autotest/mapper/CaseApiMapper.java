package com.autotest.mapper;

import com.autotest.domain.CaseApi;
import com.autotest.dto.CaseApiDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：接口用例步骤数据访问
 * 用途：批量新增、删除、按用例ID查询步骤列表
 */
@Mapper
public interface CaseApiMapper {
    /**
     * 批量新增接口用例步骤
     * 
     *     @param caseApis // 接口步骤列表
     *     @return void    // 无返回
     */
    void addCaseApi(List<CaseApi> caseApis);

    /**
     * 删除用例下全部接口步骤
     * 
     *     @param caseId // 用例ID
     *     @return void  // 无返回
     */
    void deleteCaseApi(String caseId);

    /**
     * 查询用例的接口步骤列表
     * 
     *     @param caseId            // 用例ID
     *     @return List<CaseApiDTO> // 接口步骤扩展DTO列表
     */
    List<CaseApiDTO> getCaseApiList(String caseId);
}
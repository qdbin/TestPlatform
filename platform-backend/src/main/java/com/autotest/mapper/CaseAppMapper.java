package com.autotest.mapper;

import com.autotest.domain.CaseApp;
import com.autotest.dto.CaseAppDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：App用例步骤数据访问
 * 用途：批量新增、删除、按用例ID与系统类型查询步骤列表
 */
@Mapper
public interface CaseAppMapper {
    /**
     * 批量新增App用例步骤
     * 
     *     @param caseApps // App步骤列表
     *     @return void    // 无返回
     */
    void addCaseApp(List<CaseApp> caseApps);

    /**
     * 删除用例下全部App步骤
     * 
     *     @param caseId // 用例ID
     *     @return void  // 无返回
     */
    void deleteCaseApp(String caseId);

    /**
     * 查询用例的App步骤列表
     * 
     *     @param caseId             // 用例ID
     *     @param caseType           // 系统类型（android/apple）
     *     @return List<CaseAppDTO> // App步骤扩展DTO列表
     */
    List<CaseAppDTO> getCaseAppList(String caseId, String caseType);
}
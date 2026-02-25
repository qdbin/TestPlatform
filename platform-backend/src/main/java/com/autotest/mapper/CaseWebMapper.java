package com.autotest.mapper;

import com.autotest.domain.CaseWeb;
import com.autotest.dto.CaseWebDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：Web用例步骤数据访问
 * 用途：批量新增、删除、按用例ID与类型查询步骤列表
 */
@Mapper
public interface CaseWebMapper {
    /**
     * 批量新增Web用例步骤
     * 
     *     @param caseWebs // Web步骤列表
     *     @return void    // 无返回
     */
    void addCaseWeb(List<CaseWeb> caseWebs);

    /**
     * 删除用例下全部Web步骤
     * 
     *     @param caseId // 用例ID
     *     @return void  // 无返回
     */
    void deleteCaseWeb(String caseId);

    /**
     * 查询用例的Web步骤列表
     * 
     *     @param caseId             // 用例ID
     *     @param caseType           // 用例类型（web）
     *     @return List<CaseWebDTO> // Web步骤扩展DTO列表
     */
    List<CaseWebDTO> getCaseWebList(String caseId, String caseType);
}
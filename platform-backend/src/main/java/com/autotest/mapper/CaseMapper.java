package com.autotest.mapper;

import com.autotest.domain.Case;
import com.autotest.dto.CaseDTO;
import com.autotest.request.QueryRequest;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：用例数据访问
 * 用途：提供用例的新增/更新/逻辑删除、系统类型查询、详情与列表查询
 */
@Mapper
public interface CaseMapper {
    /**
     * 新增用例
     * 
     *     @param testcase // 用例实体
     *     @return void    // 无返回
     */
    void addCase(Case testcase);

    /**
     * 更新用例
     * 
     *     @param testcase // 用例实体
     *     @return void    // 无返回
     */
    void updateCase(Case testcase);

    /**
     * 逻辑删除用例
     * 
     *     @param id // 用例ID
     *     @return void // 无返回
     */
    void deleteCase(String id);

    /**
     * 查询用例系统类型
     * 
     *     @param id     // 用例ID
     *     @return String // 系统类型（web/app/android/apple等）
     */
    String getCaseSystem(String id);

    /**
     * 获取用例详情
     * 
     *     @param id       // 用例ID
     *     @return CaseDTO // 用例扩展DTO（含模块信息等）
     */
    CaseDTO getCaseDetail(String id);

    /**
     * 查询用例列表（按条件与排序）
     * 
     *     @param request            // 查询请求（项目ID、模块ID、创建人、类型、系统、模糊条件）
     *     @return List<CaseDTO>     // 用例扩展DTO列表
     */
    List<CaseDTO> getCaseList(QueryRequest request);
}
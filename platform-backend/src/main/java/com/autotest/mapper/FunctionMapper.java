package com.autotest.mapper;

import com.autotest.domain.Function;
import com.autotest.dto.FunctionDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：函数数据访问
 * 用途：提供函数的增删改查接口，部分方法与 XML 映射绑定。
 */
@Mapper
public interface FunctionMapper {
    /**
     * 新增函数
     *
     * @param function // 函数实体（含名称/来源/入参/表达式/项目ID等）
     * @return void    // 无返回
     */
    void addFunction(Function function);

    /**
     * 更新函数
     *
     * @param function // 函数实体（根据id更新描述、表达式、入参等）
     * @return void    // 无返回
     */
    void updateFunction(Function function);

    /**
     * 根据项目与名称查询函数（用于重名校验）
     *
     * @param projectId // 项目ID
     * @param name      // 函数名称
     * @return Function // 命中则返回函数实体，否则为null
     */
    Function getFunctionByName(String projectId, String name);

    /**
     * 查询函数详情
     *
     * @param id        // 函数ID
     * @return Function // 函数实体详情
     */
    Function getFunctionDetail(String id);

    /**
     * 查询项目下自定义函数列表
     *
     * @param projectId     // 项目ID
     * @return List<Function> // 自定义函数列表（from=custom）
     */
    List<Function> getCustomFunctionList(String projectId);

    /**
     * 删除函数（逻辑删除）
     *
     * @param id   // 函数ID
     * @return void // 无返回
     */
    void deleteFunction(String id);

    /**
     * 分页查询函数列表（含用户名扩展）
     *
     * @param projectId // 项目ID（包含 system 来源的全局函数）
     * @param condition // 名称模糊查询条件（可为空）
     * @return List<FunctionDTO> // 函数扩展DTO列表
     */
    List<FunctionDTO> getFunctionList(String projectId, String condition);
}
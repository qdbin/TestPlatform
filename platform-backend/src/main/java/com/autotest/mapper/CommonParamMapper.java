package com.autotest.mapper;

import com.autotest.domain.ParamData;
import com.autotest.domain.ParamGroup;
import com.autotest.dto.ParamDataDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：公共参数与参数组数据访问
 * 用途：保存/删除参数，按组与名称查询，分页列表与批量新增参数组
 */
@Mapper
public interface CommonParamMapper {
    /**
     * 保存参数数据（新增或更新）
     *
     * @param paramData // 参数实体（包含组ID、名称、值、项目ID等）
     * @return void     // 无返回
     */
    void saveParamData(ParamData paramData);

    /**
     * 删除参数数据
     *
     * @param id    // 参数ID
     * @return void // 无返回
     */
    void deleteParamData(String id);

    /**
     * 根据组ID与参数名称查询参数
     *
     * @param groupId // 参数组ID
     * @param name    // 参数名称
     * @return ParamData // 命中返回参数实体，否则为null
     */
    ParamData getParamByGroupAndName(String groupId, String name);

    /**
     * 根据参数ID查询参数
     *
     * @param id        // 参数ID
     * @return ParamData // 参数实体
     */
    ParamData getParamById(String id);

    /**
     * 查询参数列表（按组与关键字）
     *
     * @param groupId   // 参数组ID
     * @param condition // 关键字（名称模糊匹配）
     * @return List<ParamDataDTO> // 参数扩展DTO列表
     */
    List<ParamDataDTO> getParamDataList(String groupId, String condition);

    /**
     * 根据组名称与项目ID查询参数列表
     *
     * @param groupName // 参数组名称
     * @param projectId // 项目ID
     * @return List<ParamDataDTO> // 参数扩展DTO列表
     */
    List<ParamDataDTO> getParamDataListByGroupName(String groupName, String projectId);

    /**
     * 查询项目下自定义参数列表
     *
     * @param projectId        // 项目ID
     * @return List<ParamData> // 自定义参数列表
     */
    List<ParamData> getCustomParamList(String projectId);

    /**
     * 查询项目下参数组列表
     *
     * @param projectId         // 项目ID
     * @return List<ParamGroup> // 参数组列表
     */
    List<ParamGroup> getParamGroupList(String projectId);

    /**
     * 批量新增参数组
     *
     * @param paramGroups // 参数组列表
     * @return void       // 无返回
     */
    void insertParamGroup(List<ParamGroup> paramGroups);
}
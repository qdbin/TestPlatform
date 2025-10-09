package com.autotest.mapper;

import com.autotest.domain.Engine;
import com.autotest.dto.EngineDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：执行引擎管理
 * 职责：维护引擎（保存、删除、状态/心跳更新），按名称/ID查询与列表检索。
 */
@Mapper
public interface EngineMapper {
    /**
     * 保存引擎（新增或更新）
     * @param engine 引擎实体
     */
    void saveEngine(Engine engine);

    /**
     * 删除引擎
     * @param id 引擎ID
     */
    void deleteEngine(String id);

    /**
     * 更新引擎状态
     * @param id     引擎ID
     * @param status 状态值（如 online/offline）
     */
    void updateStatus(String id, String status);

    /**
     * 更新引擎心跳时间
     * @param id   引擎ID
     * @param time 最近心跳时间戳
     */
    void updateHeartbeat(String id, Long time);

    /**
     * 将心跳超时的引擎置为离线
     * @param minLastHeartbeatTime 心跳超时阈值（时间戳）
     */
    void updateLostHeartbeatEngine(Long minLastHeartbeatTime);

    /**
     * 根据名称查询引擎
     * @param projectId 项目ID
     * @param name      引擎名称
     * @return Engine   引擎实体
     */
    Engine getEngineByName(String projectId, String name);

    /**
     * 按ID查询引擎详情
     * @param id 引擎ID
     * @return EngineDTO 引擎详情（DTO）
     */
    EngineDTO getEngineById(String id);

    /**
     * 查询项目下全部自定义引擎
     * @param projectId 项目ID
     * @return List<Engine> 引擎列表
     */
    List<Engine> getAllCustomEngine(String projectId);

    /**
     * 查询全部系统引擎
     * @return List<Engine> 系统引擎列表
     */
    List<Engine> getAllSystemEngine();

    /**
     * 条件查询引擎列表
     * @param projectId 项目ID
     * @param condition 关键字（支持模糊）
     * @return List<EngineDTO> 引擎列表（DTO）
     */
    List<EngineDTO> getEngineList(String projectId, String condition);
}
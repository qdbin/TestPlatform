package com.autotest.mapper;

import com.autotest.domain.Task;
import com.autotest.dto.TaskDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：任务调度与查询
 * 职责：新增任务、更新任务状态与引擎归属，查询列表与待执行任务。
 */
@Mapper
public interface TaskMapper {
    /**
     * 新增任务
     * @param task 任务实体
     */
    void addTask(Task task);

    /**
     * 更新任务状态
     * @param status 状态值（如 prepared/running/done）
     * @param id     任务ID
     */
    void updateTask(String status, String id);

    /**
     * 将任务分配到指定引擎（仅在当前为 system 时）
     * @param engineId 引擎ID
     * @param id       任务ID
     * @return int     受影响行数
     */
    int updateTaskEngine(String engineId, String id);

    /**
     * 批量更新指定引擎下任务状态（prepared/running）
     * @param status   新状态
     * @param engineId 引擎ID
     */
    void updateEngineAllTask(String status, String engineId);

    /**
     * 查询引擎下任务列表
     * @param engineId 引擎ID
     * @return List<TaskDTO> 任务列表（DTO）
     */
    List<TaskDTO> getTaskList(String engineId);

    /**
     * 查询任务详情
     * @param id 任务ID
     * @return TaskDTO 任务详情（DTO）
     */
    TaskDTO getTaskDetail(String id);

    /**
     * 查询待执行任务（为指定引擎挑选）
     * @param engineId 引擎ID
     * @return TaskDTO 待执行任务（DTO）
     */
    TaskDTO getToRunTask(String engineId);
}
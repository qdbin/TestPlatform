package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.EngineStatus;
import com.autotest.common.constants.EngineType;
import com.autotest.common.constants.ReportStatus;
import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Engine;
import com.autotest.domain.Task;
import com.autotest.mapper.EngineMapper;
import com.autotest.mapper.ReportMapper;
import com.autotest.mapper.TaskMapper;
import com.autotest.dto.EngineDTO;
import com.autotest.dto.TaskDTO;
import com.autotest.websocket.config.WsSessionManager;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;

/**
 * 服务：执行引擎管理
 * 职责：保存/删除引擎、停止任务、查询详情与列表；维护引擎默认类型与状态，
 *      并在停止任务时通过 WebSocket 通知对应引擎执行停止动作。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class EngineService {

    @Resource
    private EngineMapper engineMapper; // 引擎数据访问

    @Resource
    private TaskMapper taskMapper; // 任务数据访问

    @Resource
    private ReportMapper reportMapper; // 报告数据访问

    /**
     * 功能：保存引擎（新增或更新）
     *
     * @param engine 引擎实体
     * @return 引擎实体（含生成的 ID 与密钥等）
     * @throws DuplicateException 当同一项目下存在重名引擎时抛出
     */
    public Engine saveEngine(Engine engine) {
        Engine oldEngine = engineMapper.getEngineByName(engine.getProjectId(), engine.getName());
        if(oldEngine != null){
            throw new DuplicateException("当前项目已有重名引擎");
        }
        engine.setId(UUID.randomUUID().toString().replace("-", ""));
        engine.setSecret(UUID.randomUUID().toString().replace("-",""));
        engine.setEngineType(EngineType.CUSTOM.toString()); // 默认注册自定义引擎
        engine.setStatus(EngineStatus.OFFLINE.toString());  // 默认离线状态
        engine.setCreateTime(System.currentTimeMillis());
        engine.setUpdateTime(System.currentTimeMillis());
        engine.setCreateUser(engine.getUpdateUser());
        engineMapper.saveEngine(engine);

        return engine;
    }

    /**
     * 删除引擎
     * 功能：根据引擎ID删除记录
     *
     * @param engine // 引擎实体（仅使用 ID）
     */
    public void deleteEngine(Engine engine) {engineMapper.deleteEngine(engine.getId()); // 删除引擎
    }

    /**
     * 停止引擎任务
     * 功能：中断指定任务，维护引擎在线状态，并通过 WebSocket 通知停止
     *
     * @param task // 任务实体（需包含任务 ID 与引擎 ID）
     */
    public void stopEngineTask(Task task) {
        // 步骤：
        // 1) 更新报告状态为中断
        // 2) 更新任务状态为中断
        // 3) 查询引擎并依据心跳维护在线/离线状态
        // 4) 通过 WebSocket 发送停止指令
        
        // 更新报告与任务状态为中断
        reportMapper.updateReportStatusByTask(ReportStatus.DISCONTINUE.toString(), task.getId()); // 报告中断
        taskMapper.updateTask(ReportStatus.DISCONTINUE.toString(), task.getId()); // 任务中断
        Engine engine = engineMapper.getEngineById(task.getEngineId());

        // 依据最后一次心跳使时间维护引擎在线/离线状态
        if(engine.getLastHeartbeatTime()!=null &&
                (System.currentTimeMillis()-engine.getLastHeartbeatTime()) < 3*60*1000){
            engineMapper.updateStatus(task.getEngineId(), EngineStatus.ONLINE.toString()); // 在线
        }else {
            engineMapper.updateStatus(task.getEngineId(), EngineStatus.OFFLINE.toString()); // 离线
        }

        try {
            WebSocketSession session = WsSessionManager.get("engine", engine.getId()); // 获取引擎会话
            JSONObject message = new JSONObject();
            message.put("type", "stop"); // 指令：停止
            message.put("data", task.getId()); // 目标任务ID
            session.sendMessage(new TextMessage(message.toString())); // 发送停止指令
        }catch (Exception ignored){
        }
    }

    /**
     * 停止指定引擎的所有任务
     * 功能：批量中断任务与报告，并通知引擎执行停止所有任务动作
     *
     * @param engineId // 引擎ID
     */
    public void stopEngineAllTask(String engineId) {
        // 批量更新报告与任务状态为中断
        reportMapper.updateAllReportStatusByEngine(ReportStatus.DISCONTINUE.toString(), engineId); // 报告中断
        taskMapper.updateEngineAllTask(ReportStatus.DISCONTINUE.toString(), engineId); // 任务中断
        // 查询引擎并依据心跳维护在线/离线状态
        Engine engine = engineMapper.getEngineById(engineId);
        if(engine.getLastHeartbeatTime()!=null &&
                (System.currentTimeMillis()-engine.getLastHeartbeatTime()) < 3*60*1000){
            engineMapper.updateStatus(engineId, EngineStatus.ONLINE.toString()); // 在线
        }else {
            engineMapper.updateStatus(engineId, EngineStatus.OFFLINE.toString()); // 离线
        }
        // 通过 WebSocket 发送停止所有任务指令
        try {
            WebSocketSession session = WsSessionManager.get("engine", engine.getId()); // 获取会话
            JSONObject message = new JSONObject();
            message.put("type", "stopAll"); // 指令：停止所有
            session.sendMessage(new TextMessage(message.toString())); // 发送指令
        }catch (Exception ignored){
        }
    }

    /**
     * 功能：按 ID 查询引擎详情
     *
     * @param id 引擎 ID
     * @return 引擎详情（含当前任务列表）
     */
    public EngineDTO getEngineById(String id){
        EngineDTO engineDTO =  engineMapper.getEngineById(id);
        List<TaskDTO> taskDTOS = taskMapper.getTaskList(id);
        engineDTO.setTaskList(taskDTOS);
        return engineDTO;
    }

    /**
     * 功能：查询项目下所有自定义引擎，并在列表首部追加“系统引擎”占位项
     *
     * @param projectId 项目 ID
     * @return 引擎列表
     */
    public List<Engine> getAllCustomEngine(String projectId){
        List<Engine> engineList = engineMapper.getAllCustomEngine(projectId);
        Engine engine = new Engine();
        engine.setId(EngineType.SYSTEM.toString());
        engine.setName("系统引擎");
        engineList.add(0, engine);
        return engineList;
    }

    /**
     * 功能：查询引擎列表（支持关键字模糊检索）
     *
     * @param projectId 项目 ID
     * @param condition 关键字（非空时按 LIKE 模糊匹配）
     * @return 引擎列表（DTO）
     */
    public List<EngineDTO> getEngineList(String projectId, String condition){
        if(condition != null && !condition.equals("")){
            condition = ("%"+condition+"%");
        }
        return engineMapper.getEngineList(projectId, condition);
    }


}

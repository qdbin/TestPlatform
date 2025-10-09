package com.autotest.dto;

import com.autotest.domain.Engine;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * DTO：引擎扩展视图（继承 Engine）
 * 用途：追加展示所需的用户名与当前任务列表信息。
 */
@Getter
@Setter
public class EngineDTO extends Engine {

    private String username; // 更新人或负责人名称（展示）

    List<TaskDTO> taskList;  // 引擎当前关联任务列表

}

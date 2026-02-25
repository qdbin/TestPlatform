package com.autotest.service;

import com.autotest.domain.Control;
import com.autotest.mapper.ControlMapper;
import com.autotest.dto.ControlDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;

@Service
@Transactional(rollbackFor = Exception.class)
/**
 * 服务：控件管理
 * 
 *     职责：提供控件的新增/更新、删除、模块控件列表与分页列表查询。
 *     说明：保存时维护时间与创建人字段，列表查询对条件做模糊包装。
 */
public class ControlService {

    @Resource
    private ControlMapper controlMapper;

    /**
     * 保存控件（新增或更新）
     * 
     *     @param control // 控件实体（含名称/归属模块/项目ID/系统等）
     *     @return void   // 无返回
     * 
     *     关键点：
     *         - 当id为空或空串时，视为新增，生成UUID并维护时间与创建人
     *         - 否则为更新，仅刷新更新时间
     */
    public void saveControl(Control control) {
        if(control.getId().equals("") || control.getId() == null){ // 新增控件
            control.setId(UUID.randomUUID().toString());
            control.setCreateTime(System.currentTimeMillis());
            control.setUpdateTime(System.currentTimeMillis());
            control.setCreateUser(control.getUpdateUser());
            control.setStatus("Normal");
            controlMapper.addControl(control);
        }else{ // 修改控件
            control.setUpdateTime(System.currentTimeMillis());
            controlMapper.updateControl(control);
        }
    }

    /**
     * 删除控件（逻辑删除或物理删除依XML定义而定）
     * 
     *     @param control // 控件实体（使用id进行删除）
     *     @return void   // 无返回
     */
    public void deleteControl(Control control) {
        controlMapper.deleteControl(control.getId());
    }

    /**
     * 查询模块下控件列表
     * 
     *     @param projectId // 项目ID
     *     @param moduleId  // 模块ID
     *     @param system    // 系统类型（web/app/android/apple）
     *     @return List<Control> // 控件列表
     */
    public List<Control> getModuleControlList(String projectId, String moduleId, String system) {
        return controlMapper.getModuleControlList(projectId, moduleId, system);
    }

    /**
     * 分页查询控件列表（支持名称等模糊条件）
     * 
     *     @param request             // 查询请求（项目/模块/系统/条件）
     *     @return List<ControlDTO>   // 控件扩展DTO列表
     */
    public List<ControlDTO> getControlList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return controlMapper.getControlList(request);
    }

}

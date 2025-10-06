package com.autotest.controller;

import com.autotest.dto.ModuleDTO;
import com.autotest.service.ModuleService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：模块入口
 * 用途：保存、删除、树列表查询
 */
@RestController
@RequestMapping("/autotest/module")
public class ModuleController {

    @Resource
    private ModuleService moduleService;

    /**
     * 保存模块
     *
     *     @param moduleDTO // 模块DTO
     *     @param request   // Http请求上下文
     *     @return ModuleDTO // 保存后的模块DTO
     */
    @PostMapping("/save")
    public ModuleDTO save(@RequestBody ModuleDTO moduleDTO, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        moduleDTO.setUpdateUser(user); // 注入更新人
        return moduleService.save(moduleDTO); // 调用服务保存
    }

    /**
     * 删除模块
     *
     *     @param moduleDTO // 模块DTO（含id/moduleType）
     *     @return void     // 无返回
     */
    @PostMapping("/delete")
    public void delete(@RequestBody ModuleDTO moduleDTO) {
        moduleService.delete(moduleDTO); // 调用服务删除
    }

    /**
     * 获取模块树列表
     *
     *     @param moduleType     // 模块类型
     *     @param projectId      // 项目ID
     *     @return List<ModuleDTO> // 根节点列表（含children）
     */
    @GetMapping("/list/{moduleType}/{projectId}")
    public List<ModuleDTO> getModuleList(@PathVariable String moduleType, @PathVariable String projectId) {
        return moduleService.getModuleList(moduleType, projectId); // 调用服务查询
    }

}

package com.autotest.controller;

import com.autotest.domain.Database;
import com.autotest.dto.DatabaseDTO;
import com.autotest.service.DatabaseService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：数据库配置入口
 * 用途：保存、删除、名称查询、列表查询
 */
@RestController
@RequestMapping("/autotest/database")
public class DatabaseController {

    @Resource
    private DatabaseService databaseService;

    /**
     * 保存数据库配置
     *
     * @param database   // 数据库DTO
     * @param request    // Http请求上下文
     * @return void      // 无返回
     */
    @PostMapping("/save")
    public void saveDatabase(@RequestBody DatabaseDTO database, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        database.setUpdateUser(user); // 注入更新人
        databaseService.saveDatabase(database); // 调用服务保存
    }

    /**
     * 删除数据库配置
     *
     * @param database  // 数据库实体（含id）
     * @return void     // 无返回
     */
    @PostMapping("/delete")
    public void deleteEnvironment(@RequestBody Database database) {
        databaseService.deleteDatabase(database); // 调用服务删除
    }

    /**
     * 获取项目下数据库键名称列表
     *
     * @param projectId     // 项目ID
     * @return List<String> // 键名称列表
     */
    @GetMapping("/name/list/{projectId}")
    public List<String> getDatabaseNameList(@PathVariable String projectId) {
        return databaseService.getDatabaseNameList(projectId); // 调用服务查询
    }

    /**
     * 获取环境下数据库列表
     *
     * @param environmentId        // 环境ID
     * @return List<DatabaseDTO>   // 数据库列表
     */
    @GetMapping("/list/{environmentId}")
    public List<DatabaseDTO> getDatabaseList(@PathVariable String environmentId) {
        return databaseService.getDatabaseList(environmentId); // 调用服务查询
    }

}
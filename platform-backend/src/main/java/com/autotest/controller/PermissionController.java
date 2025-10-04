package com.autotest.controller;

import com.autotest.dto.MenuDTO;
import com.autotest.service.PermissionService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;


/**
 * 控制器：权限与菜单入口
 * 职责：根据用户与项目返回导航菜单，并判断设置入口的权限。
 */
@RestController
@RequestMapping
public class PermissionController {

    @Resource
    private PermissionService permissionService;

    /**
     * 获取当前用户在项目下的菜单列表
     *
     * @param userId    // 用户ID（请求参数）
     * @param projectId // 项目ID（请求参数）
     * @return List<MenuDTO> // 菜单树/列表
     */
    @GetMapping("/autotest/menu/list")
    public List<MenuDTO> getMenus(@RequestParam(name="userId") String userId, @RequestParam(name = "projectId") String projectId) {
        return permissionService.getMenus(userId, projectId);
    }

    /**
     * 判断用户是否具备项目设置入口的权限
     *
     * @param userId    // 用户ID（请求参数）
     * @param projectId // 项目ID（请求参数）
     * @return Boolean  // 是否有权限
     */
    @GetMapping("/autotest/setting/permission")
    public Boolean getSettingOptionPermission(@RequestParam(name="userId") String userId, @RequestParam(name = "projectId") String projectId) {
        return permissionService.getSettingOptionPermission(userId, projectId);
    }
}

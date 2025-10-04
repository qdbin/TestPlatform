package com.autotest.service;

import com.autotest.common.constants.MenuEnum;
import com.autotest.common.constants.PermissionEnum;
import com.autotest.mapper.PermissionMapper;
import com.autotest.mapper.VersionMapper;
import com.autotest.dto.MenuDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;

/**
 * 服务：权限与菜单
 * 职责：根据用户在项目的权限生成菜单；校验设置入口权限。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class PermissionService {

    @Resource
    private VersionMapper versionMapper;

    @Resource
    private PermissionMapper permissionMapper;

    /**
     * 生成用户在项目下的菜单
     *
     * @param userId     // 用户ID
     * @param projectId  // 项目ID
     * @return List<MenuDTO> // 菜单树（父子结构）
     */
    public List<MenuDTO> getMenus(String userId, String projectId) {
        List<String> permissions = permissionMapper.getUserPermissionByProject(projectId, userId);
        List<MenuDTO> menuDTOS = new ArrayList<>();
        MenuEnum[] menuList = MenuEnum.values();
        for (MenuEnum menu:menuList){
            if(menu.father == null){
                List<MenuDTO> menus = new ArrayList<>();
                for (MenuEnum chMenu:menuList){
                    if (chMenu.father == menu){
                        if (!permissions.contains(chMenu.permission.id)){
                            continue;   // 没有该权限跳过
                        }
                        MenuDTO chMenuDTO = new MenuDTO();
                        chMenuDTO.setId(chMenu.id);
                        chMenuDTO.setName(chMenu.name);
                        chMenuDTO.setIcon(chMenu.icon);
                        chMenuDTO.setPath(chMenu.path);
                        menus.add(chMenuDTO);
                    }
                }
                if(menus.size() == 0){
                    continue;
                }
                MenuDTO menuDTO = new MenuDTO();
                menuDTO.setId(menu.id);
                menuDTO.setName(menu.name);
                menuDTO.setIcon(menu.icon);
                menuDTO.setPath(menu.path);
                menuDTO.setMenus(menus);
                menuDTOS.add(menuDTO);
            }
        }
        return menuDTOS;
    }

    /**
     * 校验用户是否拥有设置入口权限
     *
     * @param userId     // 用户ID
     * @param projectId  // 项目ID
     * @return Boolean   // 是否拥有权限
     */
    public Boolean getSettingOptionPermission(String userId, String projectId) {
        List<String> permissions = permissionMapper.getUserPermissionByProject(projectId, userId);
        return permissions.contains(PermissionEnum.SETTING_OPT.id);
    }

}

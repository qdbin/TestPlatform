package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.User;
import com.autotest.domain.UserRole;
import com.autotest.dto.RoleDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.RoleService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制器：角色管理入口
 * 职责：提供角色分页列表、角色下用户分页列表与删除用户角色绑定的接口。
 */
@RestController
@RequestMapping("/autotest/role")
public class RoleController {

    @Resource
    private RoleService roleService;

    /**
     * 分页查询角色列表
     *
     * @param goPage       页码
     * @param pageSize     每页大小
     * @param queryRequest 查询条件（项目/关键字等），会注入请求用户
     * @param request      请求上下文（用于获取 userId）
     * @return Pager<List<RoleDTO>> 分页封装的角色列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<RoleDTO>> getRoleList(@PathVariable int goPage, @PathVariable int pageSize,
                                               @RequestBody QueryRequest queryRequest, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        queryRequest.setRequestUser(user);   // 设置查询人
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, roleService.getRoleList(queryRequest));
    }

    /**
     * 分页查询角色下的用户列表
     *
     * @param goPage   页码
     * @param pageSize 每页大小
     * @param request  查询条件（项目/角色/关键字等）
     * @return Pager<List<User>> 分页封装的用户列表
     */
    @PostMapping("/user/list/{goPage}/{pageSize}")
    public Pager<List<User>> getRoleUserList(@PathVariable int goPage, @PathVariable int pageSize,
                                             @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, roleService.getRoleUserList(request));
    }

    /**
     * 删除用户与角色的绑定关系
     *
     * @param userRole 用户角色关系实体
     * @return void    无返回
     */
    @PostMapping("/user/delete")
    public void deleteRoleUser(@RequestBody UserRole userRole){
        roleService.deleteRoleUser(userRole);
    }

}

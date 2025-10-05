package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Project;
import com.autotest.domain.Role;
import com.autotest.domain.User;
import com.autotest.domain.UserProject;
import com.autotest.dto.ProjectDTO;
import com.autotest.request.ProjectUserRequest;
import com.autotest.request.QueryRequest;
import com.autotest.service.ProjectService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
    * 控制器：项目管理接口
    * 职责：提供项目基本信息、成员管理、分页列表等接口
    */
@RestController
@RequestMapping("/autotest/project")
public class ProjectController {

    @Resource
    private ProjectService projectService;

    /**
        * 功能：获取指定用户的项目列表
        *
        * @param userId  // 用户ID
        * @return List<Project>  // 用户参与的项目集合
        */
    @GetMapping("/user/{userId}")
    public List<Project> getUserProject(@PathVariable String userId) {
        return projectService.getUserProject(userId);
    }

    /**
        * 功能：获取项目信息
        *
        * @param projectId  // 项目ID
        * @return Project   // 项目基础信息
        */
    @GetMapping("/info")
    public Project getProjectInfo(@RequestParam String projectId) {
        return projectService.getProjectInfo(projectId);
    }

    /**
        * 功能：新增项目
        *
        * @param project  // 项目实体
        * @return void    // 无返回
        */
    @PostMapping("/add")
    public void saveProject(@RequestBody Project project){
        projectService.saveProject(project);
    }

    /**
        * 功能：保存或更新项目成员关系
        *
        * @param request  // 项目与用户的绑定请求体
        * @return void    // 无返回
        */
    @PostMapping("/user/save")
    public void saveProjectUser(@RequestBody ProjectUserRequest request){
        projectService.saveProjectUser(request);
    }

    /**
        * 功能：删除项目成员
        *
        * @param request  // 项目成员关系实体（包含projectId、userId）
        * @return void    // 无返回
        */
    @PostMapping("/user/delete")
    public void deleteProjectUser(@RequestBody UserProject request){
        projectService.deleteProjectUser(request.getProjectId(), request.getUserId());
    }

    /**
        * 功能：逻辑删除项目
        *
        * @param project  // 项目实体（只需id）
        * @return void    // 无返回
        */
    @PostMapping("/delete")
    public void deleteProject(@RequestBody Project project){
        projectService.deleteProject(project.getId());
    }

    /**
        * 功能：恢复已删除项目
        *
        * @param project  // 项目实体（只需id）
        * @return void    // 无返回
        */
    @PostMapping("/recover")
    public void recoverProject(@RequestBody Project project){
        projectService.recoverProject(project.getId());
    }

    /**
        * 功能：分页查询项目列表
        *
        * @param goPage    // 页码
        * @param pageSize  // 每页大小
        * @param request   // 查询条件
        * @return Pager<List<ProjectDTO>> // 分页信息与数据集合
        */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<ProjectDTO>> getProjectList(@PathVariable int goPage, @PathVariable int pageSize,
                                                  @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, projectService.getProjectList(request));
    }

    /**
        * 功能：分页查询项目成员列表
        *
        * @param goPage       // 页码
        * @param pageSize     // 每页大小
        * @param queryRequest // 查询条件
        * @param request      // HttpServletRequest（含会话用户）
        * @return Pager<List<User>> // 分页信息与用户集合
        */
    @PostMapping("/user/list/{goPage}/{pageSize}")
    public Pager<List<User>> getProjectUserList(@PathVariable int goPage, @PathVariable int pageSize,
                                                @RequestBody QueryRequest queryRequest, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        queryRequest.setRequestUser(user);   // 设置查询人
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, projectService.getProjectUserList(queryRequest));
    }

    /**
        * 功能：获取项目角色列表
        *
        * @param projectId  // 项目ID
        * @return List<Role> // 项目下的角色集合
        */
    @GetMapping("/role/list")
    public List<Role> getProjectRoleList(@RequestParam String projectId) {
        return projectService.getProjectRoleList(projectId);
    }
}

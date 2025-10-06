package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Function;
import com.autotest.dto.FunctionDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.FunctionService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制层：函数管理
 * 范围：提供函数的保存、删除、详情与列表查询接口，保持注释增量更新与合理密度。
 */
@RestController
@RequestMapping("/autotest/function")
public class FunctionController {

    @Resource
    private FunctionService functionService;

    /**
     * 保存函数（新增或更新）
     *
     *     @param function // 函数实体（JSON），名称/来源/入参/表达式/项目ID等
     *     @param request  // Http请求（注入用户上下文）
     *     @return void    // 无返回
     */
    @PostMapping("/save")
    public void saveFunction(@RequestBody Function function, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        function.setUpdateUser(user);
        functionService.saveFunction(function);
    }

    /**
     * 删除函数（逻辑删除）
     *
     *     @param function // 函数实体（仅使用id）
     *     @return void    // 无返回
     */
    @PostMapping("/delete")
    public void deleteFunction(@RequestBody Function function) {
        functionService.deleteFunction(function.getId());
    }

    /**
     * 获取函数详情（查看函数）
     *
     *     @param functionId // 函数ID
     *     @return Function  // 函数实体详情
     */
    @GetMapping("/detail/{functionId}")
    public Function getFunctionDetail(@PathVariable String functionId) {
        return functionService.getFunctionDetail(functionId);
    }

    /**
     * 查询项目下自定义函数列表
     *
     *     @param projectId         // 项目ID
     *     @return List<Function>   // 自定义函数列表
     */
    @GetMapping("/custom/list/{projectId}")
    public List<Function> getCustomFunctionList(@PathVariable String projectId) {
        return functionService.getCustomFunctionList(projectId);
    }

    /**
     * 分页查询函数列表（含创建人用户名）
     *
     * 关键点：
     * - 使用分页拦截器 PageHelper 统一分页
     * - 返回 Pager 携带分页信息与数据列表
     *
     *     @param goPage    // 页码
     *     @param pageSize  // 每页大小
     *     @param request   // 查询条件（项目ID与模糊条件）
     *     @return Pager<List<FunctionDTO>> // 分页信息与函数扩展DTO列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<FunctionDTO>> getFunctionList(@PathVariable int goPage, @PathVariable int pageSize,
                                                    @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, functionService.getFunctionList(request));
    }
}

package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Element;
import com.autotest.dto.ElementDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.ElementService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：页面元素入口
 * 用途：保存、删除、详情与分页列表查询
 */
@RestController
@RequestMapping("/autotest/element")
public class ElementController {

    @Resource
    private ElementService elementService;

    /**
     * 保存页面元素
     *
     * @param element   // 元素实体
     * @param request   // Http请求上下文
     * @return void     // 无返回
     */
    @PostMapping("/save")
    public void saveElement(@RequestBody Element element, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        element.setUpdateUser(user); // 注入更新人
        elementService.saveElement(element); // 调用服务保存
    }

    /**
     * 删除页面元素
     *
     * @param element  // 元素实体（含id）
     * @return void    // 无返回
     */
    @PostMapping("/delete")
    public void deleteElement(@RequestBody Element element) {
        elementService.deleteElement(element); // 调用服务删除
    }

    /**
     * 查询模块下元素列表
     *
     * @param request  // 查询条件载体（含项目/模块）
     * @return List<Element> // 元素列表
     */
    @PostMapping("/list/module")
    public List<Element> getElementDetail(@RequestBody QueryRequest request){
        return elementService.getModuleElementList(request.getProjectId(), request.getModuleId()); // 调用服务查询
    }

    /**
     * 分页查询元素列表
     *
     * @param goPage     // 页码
     * @param pageSize   // 每页数量
     * @param request    // 查询条件载体
     * @return Pager<List<ElementDTO>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<ElementDTO>> getElementList(@PathVariable int goPage, @PathVariable int pageSize,
                                          @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true); // 启动分页
        return PageUtils.setPageInfo(page, elementService.getElementList(request)); // 设置分页信息
    }
}
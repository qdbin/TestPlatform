package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Control;
import com.autotest.dto.ControlDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.ControlService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：控件管理入口
 * 职责：保存、删除、模块控件查询与分页列表
 */
@RestController
@RequestMapping("/autotest/control")
public class ControlController {

    @Resource
    private ControlService controlService;

    /**
     * 功能：保存控件
     *
     * @param control  // 控件实体
     * @param request  // Http请求上下文（注入更新人）
     * @return void    // 无返回
     */
    @PostMapping("/save")
    public void saveControl(@RequestBody Control control, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        control.setUpdateUser(user);
        controlService.saveControl(control);
    }

    /**
     * 功能：删除控件
     *
     * @param control // 控件实体（仅使用id）
     * @return void   // 无返回
     */
    @PostMapping("/delete")
    public void deleteControl(@RequestBody Control control) {
        controlService.deleteControl(control);
    }

    /**
     * 功能：查询模块下控件列表
     *
     * @param request // 查询条件（项目/模块/系统类型）
     * @return List<Control> // 控件列表
     */
    @PostMapping("/list/module")
    public List<Control> getControlDetail(@RequestBody QueryRequest request){
        return controlService.getModuleControlList(request.getProjectId(), request.getModuleId(), request.getSystem());
    }

    /**
     * 功能：分页查询控件列表
     *
     * @param goPage   // 页码
     * @param pageSize // 每页大小
     * @param request  // 查询条件载体
     * @return Pager<List<ControlDTO>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<ControlDTO>> getControlList(@PathVariable int goPage, @PathVariable int pageSize,
                                          @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, controlService.getControlList(request));
    }
}

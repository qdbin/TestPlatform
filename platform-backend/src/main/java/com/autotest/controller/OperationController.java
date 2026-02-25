package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Operation;
import com.autotest.dto.OperationDTO;
import com.autotest.dto.OperationGroupDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.OperationService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制器：操作管理入口
 * 用途：提供操作的保存、删除、详情、分组与分页列表接口。
 */
@RestController
@RequestMapping("/autotest/operation")
public class OperationController {

    @Resource
    private OperationService operationService;

    /**
     * 保存操作
     * 
     *     @param operation // 操作实体（含元素/数据/代码等）
     *     @param request   // Http请求（注入用户上下文）
     *     @return void     // 无返回
     */
    @PostMapping("/save")
    public void saveOperation(@RequestBody Operation operation, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        operation.setUpdateUser(user);
        operationService.saveOperation(operation);
    }

    /**
     * 删除操作（软删除）
     * 
     *     @param operation // 操作实体（含id/uiType）
     *     @return void     // 无返回
     */
    @PostMapping("/delete")
    public void deleteOperation(@RequestBody Operation operation) {
        operationService.deleteOperation(operation.getId(), operation.getUiType());
    }

    /**
     * 获取操作详情
     * 
     *     @param uiType       // UI类型（web/app）
     *     @param operationId  // 操作ID
     *     @return Operation   // 操作实体详情
     */
    @GetMapping("/detail/{uiType}/{operationId}")
    public Operation getOperationDetail(@PathVariable String uiType, @PathVariable String operationId) {
        return operationService.getOperationDetail(operationId, uiType);
    }

    /**
     * 获取分组操作列表
     * 
     *     @param uiType    // UI类型
     *     @param system    // 系统标识（app）
     *     @param projectId // 项目ID
     *     @return List<OperationGroupDTO> // 分组下的操作列表
     */
    @GetMapping("/group/{uiType}/list/{projectId}")
    public List<OperationGroupDTO> getGroupOperationList(@PathVariable String uiType,@RequestParam String system, @PathVariable String projectId) {
        return operationService.getGroupOperationList(uiType, system, projectId);
    }

    /**
     * 分页查询操作列表
     * 
     *     @param goPage   // 页码
     *     @param pageSize // 每页大小
     *     @param request  // 查询条件（项目/类型/系统/模糊条件等）
     *     @return Pager<List<OperationDTO>> // 分页信息与数据列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<OperationDTO>> getOperationList(@PathVariable int goPage, @PathVariable int pageSize,
                                                    @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, operationService.getOperationList(request));
    }
}

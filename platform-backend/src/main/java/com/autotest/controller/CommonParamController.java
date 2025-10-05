package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.ParamData;
import com.autotest.domain.ParamGroup;
import com.autotest.dto.ParamDataDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.CommonParamService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：公共参数管理
 * 职责：参数数据的新增/删除、分页查询、按分组与项目维度查询。
 */
@RestController
@RequestMapping("/autotest/commonParam")
public class CommonParamController {

    @Resource
    private CommonParamService commonParamService;

    /**
     * 保存参数数据（新增或更新），并记录更新人
     *
     * @param paramData // 参数数据实体
     * @param request   // 请求上下文（用于获取userId）
     * @return void     // 无返回
     */
    @PostMapping("/param/save")
    public void saveParamData(@RequestBody ParamData paramData, HttpServletRequest request) {
        // 赋值更新用户
        String user = request.getSession().getAttribute("userId").toString();
        paramData.setUpdateUser(user);
        commonParamService.saveParamData(paramData);
    }

    /**
     * 删除参数数据
     *
     * @param paramData // 参数数据实体（至少包含id）
     * @return void     // 无返回
     */
    @PostMapping("/param/delete")
    public void deleteParamData(@RequestBody ParamData paramData) {
        commonParamService.deleteParamData(paramData);
    }

    /**
     * 分页查询指定分组的参数数据
     *
     * @param goPage   // 页码
     * @param pageSize // 每页大小
     * @param groupId  // 分组ID
     * @param request  // 查询条件（关键字等）
     * @return Pager<List<ParamDataDTO>> // 分页结果
     */
    @PostMapping("/param/{groupId}/list/{goPage}/{pageSize}")
    public Pager<List<ParamDataDTO>> getParamDataList(@PathVariable int goPage, @PathVariable int pageSize,
                                                      @PathVariable String groupId, @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, commonParamService.getParamDataList(groupId, request.getCondition()));
    }

    /**
     * 按分组名称与项目查询参数数据
     *
     * @param groupName // 分组名称
     * @param projectId // 项目ID
     * @return List<ParamDataDTO> // 参数数据列表
     */
    @GetMapping("/param/list/{groupName}/{projectId}")
    public List<ParamDataDTO> getParamDataList(@PathVariable String groupName, @PathVariable String projectId) {
        return commonParamService.getParamDataListByGroupName(groupName, projectId);
    }

    /**
     * 查询项目下的自定义参数列表
     *
     * @param projectId // 项目ID
     * @return List<ParamData> // 自定义参数列表
     */
    @GetMapping("/custom/list/{projectId}")
    public List<ParamData> getCustomParamList(@PathVariable String projectId) {
        return commonParamService.getCustomParamList(projectId);
    }

    /**
     * 查询项目下的参数分组列表
     *
     * @param projectId // 项目ID
     * @return List<ParamGroup> // 参数分组列表
     */
    @GetMapping("/group/list/{projectId}")
    public List<ParamGroup> getParamGroupList(@PathVariable String projectId) {
        return commonParamService.getParamGroupList(projectId);
    }
}

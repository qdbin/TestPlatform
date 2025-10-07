package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.dto.ApiDTO;
import com.autotest.request.ApiRequest;
import com.autotest.request.QueryRequest;
import com.autotest.service.ApiService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 控制器：接口定义入口
 * 用途：保存、删除、详情、列表分页查询
 */
@RestController
@RequestMapping("/autotest/api")
public class ApiController {

    @Resource
    private ApiService apiService;

    /**
     * 保存接口定义
     *
     * @param apiRequest   // 请求载体
     * @param request      // Http请求上下文
     * @return String      // 接口ID
     */
    @PostMapping("/save")
    public String saveApi(@RequestBody ApiRequest apiRequest, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        apiRequest.setUpdateUser(user); // 注入更新人
        return apiService.saveApi(apiRequest); // 调用服务保存
    }

    /**
     * 删除接口定义
     *
     * @param request   // 请求载体（含id）
     * @return void     // 无返回
     */
    @PostMapping("/delete")
    public void deleteApi(@RequestBody ApiRequest request) {
        apiService.deleteApi(request); // 调用服务删除
    }

    /**
     * 获取接口详情
     *
     * @param apiId    // 接口主键ID
     * @return ApiDTO  // 详情数据
     */
    @GetMapping("/detail/{apiId}")
    public ApiDTO getApiDetail(@PathVariable String apiId){
        return apiService.getApiDetail(apiId); // 调用服务查询
    }

    /**
     * 分页查询接口列表
     *
     * @param goPage     // 页码
     * @param pageSize   // 每页数量
     * @param request    // 查询条件载体
     * @return Pager<List<ApiDTO>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<ApiDTO>> getApiList(@PathVariable int goPage, @PathVariable int pageSize,
                                          @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true); // 启动分页
        return PageUtils.setPageInfo(page, apiService.getApiList(request)); // 设置分页信息
    }
}

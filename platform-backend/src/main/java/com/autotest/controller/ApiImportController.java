package com.autotest.controller;

import com.autotest.service.ApiImportService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;

/**
 * 控制器：接口导入入口
 * 职责：接收并解析外部接口文件（如 Swagger/Postman），批量导入到指定项目与模块。
 */
@RestController
@RequestMapping("/autotest/import")
public class ApiImportController {
    @Resource
    public ApiImportService apiImportService;

    /**
     * 导入接口定义文件
     *
     * @param file      // 上传文件（multipart），包含接口定义
     * @param sourceType // 源类型（如 swagger、postman）
     * @param projectId // 目标项目ID
     * @param moduleId  // 目标模块ID
     * @param request   // 请求上下文（读取 session.userId）
     * @return void     // 无返回
     */
    @PostMapping(value="/api", consumes = {"multipart/form-data"})
    public void importApi( @RequestParam MultipartFile file, @RequestParam String
            sourceType, @RequestParam String projectId, @RequestParam String moduleId, HttpServletRequest request) {
        String userId = request.getSession().getAttribute("userId").toString();
        apiImportService.importApi(file, sourceType, projectId, moduleId, userId);
    }

}

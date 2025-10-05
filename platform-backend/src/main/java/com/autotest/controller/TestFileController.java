package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.TestFile;
import com.autotest.dto.TestFileDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.TestFileService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;


/**
 * 控制器：测试文件管理入口
 * 职责：提供测试文件与测试包的上传、删除、查询全部与分页列表接口。
 * 说明：控制器负责轻量的会话用户注入与分页包装，业务逻辑在 Service 层实现。
 */
@RestController
@RequestMapping("/autotest/file")
public class TestFileController {

    @Resource
    private TestFileService testFileService;

    /**
     * 上传测试文件（multipart/form-data）
     *
     * @param fileName   文件名称
     * @param projectId  项目ID
     * @param description 文件描述
     * @param file       上传文件（可选）
     * @param request    请求上下文（用于获取 userId 记录更新人）
     * @return void      无返回
     */
    @PostMapping(value = "/upload", consumes = {"multipart/form-data"})
    public void uploadFile(@RequestParam("name") String fileName, @RequestParam("projectId") String projectId, @RequestParam("description") String description,
                    @RequestParam(value = "file", required=false) MultipartFile file, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        TestFile testFile = new TestFile();
        testFile.setName(fileName);
        testFile.setProjectId(projectId);
        testFile.setDescription(description);
        testFile.setUpdateUser(user);
        testFileService.uploadFile(testFile, file);
    }

    /**
     * 上传测试包（multipart/form-data）（app）
     *
     * @param packageName 包名称
     * @param file        上传包文件（可选）
     * @return String     上传后的包路径或标识
     */
    @PostMapping(value = "/package/upload", consumes = {"multipart/form-data"})
    public String uploadPackage(@RequestParam("name") String packageName,
                           @RequestParam(value = "file", required=false) MultipartFile file) {
        return testFileService.uploadPackage(packageName, file);
    }

    /**
     * 删除测试文件
     *
     * @param testFile 测试文件实体（仅使用 id）
     * @return void    无返回
     */
    @PostMapping("/delete")
    public void deleteFile(@RequestBody TestFile testFile) {
        testFileService.deleteFile(testFile.getId());
    }

    /**
     * 查询项目下所有测试文件
     *
     * @param projectId 项目ID
     * @return List<TestFile> 测试文件列表
     */
    @GetMapping("/all/{projectId}")
    public List<TestFile> getAllTestFile(@PathVariable String projectId) {
        return testFileService.getAllTestFile(projectId);
    }

    /**
     * 分页查询测试文件列表
     *
     * @param goPage   页码
     * @param pageSize 每页大小
     * @param request  查询条件载体
     * @return Pager<List<TestFileDTO>> 分页封装的测试文件列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<TestFileDTO>> getTestFileList(@PathVariable int goPage, @PathVariable int pageSize,
                                          @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, testFileService.getTestFileList(request));
    }
}

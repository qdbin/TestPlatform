package com.autotest.service;

import com.autotest.common.utils.FileUtils;
import com.autotest.domain.TestFile;
import com.autotest.mapper.TestFileMapper;
import com.autotest.dto.TestFileDTO;
import com.autotest.request.QueryRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import java.text.DateFormat;
import java.util.Date;
import java.util.List;
import java.util.UUID;

/**
 * 服务：测试文件/包管理
 * 职责：上传测试文件与应用安装包、删除文件、列表查询。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class TestFileService {

    @Value("${test.file.path}")
    public String TEST_FILE_PATH;

    @Value("${app.package.path}")
    public String APP_PACKAGE_PATH;

    @Resource
    private TestFileMapper testFileMapper;

    /**
     * 上传测试文件
     *
     * @param testFile // 测试文件元数据
     * @param file     // 上传的文件流
     * @return void    // 无返回
     */
    public void uploadFile(TestFile testFile, MultipartFile file){
        // 赋值其他信息（id、createTime）
        testFile.setId(UUID.randomUUID().toString().replace("-", ""));
        testFile.setCreateTime(System.currentTimeMillis());
        testFile.setUpdateTime(System.currentTimeMillis());
        testFile.setCreateUser(testFile.getUpdateUser());
        // 保存文件
        String path = TEST_FILE_PATH + "/" + testFile.getProjectId() + "/" + testFile.getId();
        String filePath = FileUtils.uploadTestFile(file, path);
        testFile.setFilePath(filePath);
        testFileMapper.saveTestFile(testFile);
    }

    /**
     * 上传应用安装包
     *
     * @param packageName // 包名（文件名）
     * @param file        // 上传的文件流
     * @return String     // 下载地址路径
     */
    public String uploadPackage(String packageName, MultipartFile file){
        DateFormat dateInstance = DateFormat.getDateInstance();
        String date = dateInstance.format(new Date());
        // 保存文件
        String fileId = UUID.randomUUID().toString();
        String path = APP_PACKAGE_PATH + "/" + date + "/" + fileId;
        FileUtils.uploadTestFile(file, path);
        return "/openapi/download/package/" + date + "/" + fileId + "/" + packageName;
    }

    /**
     * 删除测试文件
     *
     * @param id    // 文件ID
     * @return void // 无返回
     */
    public void deleteFile(String id) {
        TestFile testFile = testFileMapper.getTestFile(id);
        FileUtils.deleteFile(testFile.getFilePath());
        testFileMapper.deleteTestFile(id);
    }

    /**
     * 查询项目下所有测试文件
     *
     * @param projectId       // 项目ID
     * @return List<TestFile> // 测试文件列表
     */
    public List<TestFile> getAllTestFile(String projectId) {
        return testFileMapper.getAllTestFile(projectId);
    }

    /**
     * 条件查询测试文件列表
     *
     * @param request              // 查询条件（含项目与关键字）
     * @return List<TestFileDTO>   // 测试文件DTO列表
     */
    public List<TestFileDTO> getTestFileList(QueryRequest request) {
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return testFileMapper.getTestFileList(request.getProjectId(), request.getCondition());
    }

}

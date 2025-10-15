package com.autotest.mapper;

import com.autotest.domain.TestFile;
import com.autotest.dto.TestFileDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射: 测试文件数据访问
 * 用途: 保存/查询/删除测试文件与条件列表检索
 */
@Mapper
public interface TestFileMapper {
    /**
     * 保存测试文件（新增或更新）
     *
     * @param testFile // 文件实体
     * @return void    // 无返回
     */
    void saveTestFile(TestFile testFile);

    /**
     * 查询测试文件详情
     *
     * @param id       // 文件ID
     * @return TestFile // 文件实体
     */
    TestFile getTestFile(String id);

    /**
     * 删除测试文件（逻辑删除）
     *
     * @param id     // 文件ID
     * @return void  // 无返回
     */
    void deleteTestFile(String id);

    /**
     * 获取项目下全部测试文件
     *
     * @param projectId      // 项目ID
     * @return List<TestFile> // 文件列表
     */
    List<TestFile> getAllTestFile(String projectId);

    /**
     * 条件查询测试文件列表(连user表查询，附加username)
     *
     * @param projectId          // 项目ID
     * @param condition          // 关键字（支持模糊）
     * @return List<TestFileDTO> // 文件列表（含创建人等扩展信息）
     */
    List<TestFileDTO> getTestFileList(String projectId, String condition);
}
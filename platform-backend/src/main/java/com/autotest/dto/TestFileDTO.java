package com.autotest.dto;

import com.autotest.domain.TestFile;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO：测试文件扩展视图（继承 TestFile）
 * 用途：在测试文件基础信息上补充展示所需的用户名字段。
 */
@Getter
@Setter
public class TestFileDTO extends TestFile {

    /** 用户名称（创建/更新操作者的展示名） */
    private String username;
}

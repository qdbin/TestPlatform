package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Version;
import com.autotest.mapper.VersionMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 类型: Service
 * 职责: 管理项目版本（Version）的增删查改，确保版本名称在项目内唯一
 * 高频功能: (1) 保存/更新版本 (2) 删除版本 (3) 条件查询版本列表
 *
 * 使用示例:
 *  // 保存
 *  // saveVersion(version)
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class VersionService {

    @Resource
    private VersionMapper versionMapper;

    /**
     * 保存或更新版本（同项目下版本名称唯一）
     *
     * @param version // 版本实体，包含项目ID与版本名称等信息
     *
     * 使用示例:
     *  // 入参示例: {projectId:"p1", name:"v1.0"}
     *  // 调用示例: saveVersion(version)
     *  // 返回值示例: 无返回，若重名则抛 DuplicateException
     */
    public void saveVersion(Version version) {
        Version oldVersion = versionMapper.getVersionByName(version.getProjectId(), version.getName()); // 查询重名版本
        if(oldVersion != null && !Objects.equals(oldVersion.getId(), version.getId())){
            throw new DuplicateException("当前项目已有重名版本");
        }
        if(version.getId() == null || version.getId().equals("")){
            // 新增版本
            version.setId(UUID.randomUUID().toString());
            version.setCreateTime(System.currentTimeMillis());
            version.setUpdateTime(System.currentTimeMillis());
        }else{
            // 更新版本
            version.setUpdateTime(System.currentTimeMillis());
        }
        versionMapper.saveVersion(version); // 持久化保存
    }

    /**
     * 删除版本
     *
     * @param id // 版本ID
     */
    public void deleteVersion(String id) {
        versionMapper.deleteVersion(id); // 直接删除
    }

    /**
     * 获取版本列表（可按条件模糊查询）
     *
     * @param projectId // 项目ID
     * @param condition // 模糊查询条件（版本名称），为空则查询全部
     * @return List<Version> // 版本列表
     */
    public List<Version> getVersionList(String projectId, String condition) {
        if(condition != null && !condition.equals("")){
            condition = "%"+condition+"%";
        }
        return versionMapper.getVersionList(projectId, condition); // 查询结果返回
    }

}

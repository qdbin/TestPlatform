package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Application;
import com.autotest.mapper.ApplicationMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：应用管理
 * 职责：保存（去重校验）、删除与列表查询应用信息。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class ApplicationService {

    @Resource
    private ApplicationMapper applicationMapper;

    /**
     * 保存应用信息
     * @param application // 应用实体
     * @return void       // 无返回
     */
    public void saveApplication(Application application) {
        Application oldApplication = applicationMapper.getApplicationByName(application.getProjectId(), application.getName());
        if(oldApplication != null && !Objects.equals(oldApplication.getId(), application.getId())){
            throw new DuplicateException("当前项目已有重名应用");
        }
        if(application.getId() == null || application.getId().equals("")){
            //新增版本
            application.setId(UUID.randomUUID().toString());
            application.setCreateTime(System.currentTimeMillis());
            application.setUpdateTime(System.currentTimeMillis());
        }else{
            // 更新版本
            application.setUpdateTime(System.currentTimeMillis());
        }
        applicationMapper.saveApplication(application);
    }

    /**
     * 删除应用
     * @param id    // 应用ID
     * @return void // 无返回
     */
    public void deleteApplication(String id) {
        applicationMapper.deleteApplication(id);
    }

    /**
     * 条件查询应用列表
     * @param projectId         // 项目ID
     * @param condition         // 关键字（支持模糊）
     * @param system            // 系统类型（android/apple/web等）
     * @return List<Application> // 应用列表
     */
    public List<Application> getApplicationList(String projectId, String condition, String system) {
        if(condition != null && !condition.equals("")){
            condition = "%"+condition+"%";
        }
        return applicationMapper.getApplicationList(projectId, condition, system);
    }

}

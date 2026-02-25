package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.DomainSign;
import com.autotest.mapper.DomainSignMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 类型: Service
 * 职责: 管理域名标识（DomainSign）的增删查改，保障项目内域名标识唯一性
 * 高频功能: (1) 保存/更新域名标识 (2) 删除域名标识 (3) 条件查询列表
 *
 * 使用示例:
 *  // 保存
 *  // saveDomainSign(domainSign)
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class DomainSignService {

    @Resource
    private DomainSignMapper domainSignMapper;

    /**
     * 保存或更新域名标识（同项目下名称唯一）
     *
     * @param domainSign // 域名标识实体，包含项目ID与名称等信息
     *
     * 使用示例:
     *  // 入参示例: {projectId:"p1", name:"core", ...}
     *  // 调用示例: saveDomainSign(domainSign)
     *  // 返回值示例: 无返回，若重名则抛 DuplicateException
     */
    public void saveDomainSign(DomainSign domainSign) {
        DomainSign oldDomainSign = domainSignMapper.getDomainSignByName(domainSign.getProjectId(), domainSign.getName()); // 查询重名
        if(oldDomainSign != null && !Objects.equals(oldDomainSign.getId(), domainSign.getId())){
            throw new DuplicateException("当前项目已有重名域名标识");
        }
        if(domainSign.getId() == null || domainSign.getId().equals("")){
            // 新增域名标识
            domainSign.setId(UUID.randomUUID().toString());
            domainSign.setCreateTime(System.currentTimeMillis());
            domainSign.setUpdateTime(System.currentTimeMillis());
        }else{
            // 更新域名标识
            domainSign.setUpdateTime(System.currentTimeMillis());
        }
        domainSignMapper.saveDomainSign(domainSign); // 持久化保存
    }

    /**
     * 删除域名标识
     *
     * @param id // 域名标识ID
     */
    public void deleteDomainSign(String id) {
        domainSignMapper.deleteDomainSign(id); // 直接删除
    }

    /**
     * 获取域名标识列表（可按条件模糊查询）
     *
     * @param projectId // 项目ID
     * @param condition // 模糊查询条件（名称），为空则查询全部
     * @return List<DomainSign> // 域名标识列表
     */
    public List<DomainSign> getDomainSignList(String projectId, String condition) {
        if(condition != null && !condition.equals("")){
            condition = "%"+condition+"%";
        }
        return domainSignMapper.getDomainSignList(projectId, condition); // 查询结果返回
    }

}
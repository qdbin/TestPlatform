package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Domain;
import com.autotest.mapper.DomainMapper;
import com.autotest.dto.DomainDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：域配置维护
 *     职责：重名校验；新增/更新；列表查询
 *     示例：入口 saveDomain/deleteDomain/getDomainList 进行持久化调用
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class DomainService {

    @Resource
    private DomainMapper domainMapper;

    /**
     * 保存域配置（新增或更新）
     *
     * @param domain    // 域实体（含环境/匹配键/数据等）
     * @return void     // 无返回
     *
     * 示例：
     *     入参示例：domain.id为空表示新增
     *     调用示例：domainService.saveDomain(domain)
     *     返回示例：无
     */
    public void saveDomain(Domain domain) {
        // 重名校验（同环境同匹配键不允许重复）
        Domain oldDomain = domainMapper.getDomainByName(domain.getEnvironmentId(), domain.getDomainKey());
        if(oldDomain != null && !Objects.equals(oldDomain.getId(), domain.getId())){
            throw new DuplicateException("当前环境已有重名匹配标识");
        }
        if(domain.getId() == null || domain.getId().equals("")){
            // 新增域名（初始化ID与时间戳）
            domain.setId(UUID.randomUUID().toString()); // 生成主键
            domain.setCreateTime(System.currentTimeMillis()); // 创建时间
            domain.setUpdateTime(System.currentTimeMillis()); // 更新时间
            domain.setCreateUser(domain.getUpdateUser()); // 记录创建人
        }else{
            // 更新域名
            domain.setUpdateTime(System.currentTimeMillis()); // 刷新更新时间
        }
        domainMapper.saveDomain(domain); // 持久化保存
    }

    /**
     * 删除域配置
     *
     * @param domain    // 域实体（包含id）
     * @return void     // 无返回
     */
    public void deleteDomain(Domain domain) {
        domainMapper.deleteDomain(domain.getId()); // 根据主键删除
    }

    /**
     * 查询环境下域配置列表
     *
     * @param environmentId // 环境ID
     * @return List<DomainDTO> // 域配置列表（DTO）
     */
    public List<DomainDTO> getDomainList(String environmentId){
        return domainMapper.getDomainList(environmentId); // 返回域列表
    }

}

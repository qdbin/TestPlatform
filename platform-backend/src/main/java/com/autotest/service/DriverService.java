package com.autotest.service;

import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Driver;
import com.autotest.mapper.DriverMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：驱动管理
 * 职责：保存/删除驱动配置，支持按项目与关键字检索驱动列表；
 *      保存时校验同一项目下名称唯一性，并根据是否携带 ID 区分新增或更新，维护创建/更新时间戳。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class DriverService {

    @Resource
    private DriverMapper driverMapper;

    /**
     * 功能：保存驱动配置（新增或更新）
     *
     * @param driver 驱动实体（新增不携带 ID，更新需携带 ID）
     * @throws DuplicateException 当同一项目下存在重名驱动时抛出
     */
    public void saveDriver(Driver driver) {
        Driver oldDriver = driverMapper.getDriverByName(driver.getProjectId(), driver.getName());
        if(oldDriver != null && !Objects.equals(oldDriver.getId(), driver.getId())){
            throw new DuplicateException("当前项目已有重名驱动配置");
        }
        if(driver.getId() == null || driver.getId().equals("")){
            //新增版本
            driver.setId(UUID.randomUUID().toString());
            driver.setCreateTime(System.currentTimeMillis());
            driver.setUpdateTime(System.currentTimeMillis());
        }else{
            // 更新版本
            driver.setUpdateTime(System.currentTimeMillis());
        }
        driverMapper.saveDriver(driver);
    }

    /**
     * 功能：删除驱动配置
     *
     * @param id 驱动 ID
     */
    public void deleteDriver(String id) {
        driverMapper.deleteDriver(id);
    }

    /**
     * 功能：查询项目下驱动列表（支持关键字模糊检索）
     *
     * @param projectId 项目 ID
     * @param condition 关键字（可为空；当不为空时按 LIKE 模糊匹配）
     * @return 驱动列表
     */
    public List<Driver> getDriverList(String projectId, String condition) {
        if(condition != null && !condition.equals("")){
            condition = "%"+condition+"%";
        }
        return driverMapper.getDriverList(projectId, condition);
    }

}

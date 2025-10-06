package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.exception.DuplicateException;
import com.autotest.domain.Database;
import com.autotest.mapper.DatabaseMapper;
import com.autotest.dto.DBConnectInfo;
import com.autotest.dto.DatabaseDTO;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 服务：数据库配置维护
 *     职责：保存（去重校验）；删除；名称与列表查询
 *     示例：saveDatabase -> mapper.saveDatabase；getDatabaseList 解析连接信息
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class DatabaseService {

    @Resource
    private DatabaseMapper databaseMapper;

    /**
     * 保存数据库配置（新增/更新）
     *
     * @param database   // 数据库DTO（含info）
     * @return void      // 无返回
     */
    public void saveDatabase(DatabaseDTO database) {
        Database oldDatabase = databaseMapper.getDatabaseByName(database.getEnvironmentId(), database.getDatabaseKey());
        if(oldDatabase != null && !Objects.equals(oldDatabase.getId(), database.getId())){
            throw new DuplicateException("当前环境已有重名数据库");
        }
        if(database.getId() == null || database.getId().equals("")){
            // 新增数据库
            database.setId(UUID.randomUUID().toString()); // 生成主键
            database.setConnectInfo(JSONObject.toJSONString(database.getInfo())); // 序列化连接信息
            database.setCreateTime(System.currentTimeMillis()); // 创建时间
            database.setUpdateTime(System.currentTimeMillis()); // 更新时间
            database.setCreateUser(database.getUpdateUser()); // 创建人
        }else{
            // 更新数据库
            database.setUpdateTime(System.currentTimeMillis()); // 更新时间
            database.setConnectInfo(JSONObject.toJSONString(database.getInfo())); // 序列化连接信息
        }
        databaseMapper.saveDatabase(database); // 落库
    }

    /**
     * 删除数据库配置
     *
     * @param database   // 数据库实体（含id）
     * @return void      // 无返回
     */
    public void deleteDatabase(Database database) {
        databaseMapper.deleteDatabase(database.getId()); // 根据主键删除
    }

    /**
     * 查询项目下的数据库键名称列表
     *
     * @param projectId       // 项目ID
     * @return List<String>   // 键名称列表
     */
    public List<String> getDatabaseNameList(String projectId){
        return databaseMapper.getDatabaseNameList(projectId); // 查询键列表
    }

    /**
     * 查询环境下数据库列表
     *
     * @param environmentId          // 环境ID
     * @return List<DatabaseDTO>     // 数据库列表（含解析后info）
     */
    public List<DatabaseDTO> getDatabaseList(String environmentId){
        List<DatabaseDTO> databaseDTOS = databaseMapper.getDatabaseList(environmentId);
        for(DatabaseDTO databaseDTO: databaseDTOS){
            DBConnectInfo info = JSONObject.parseObject(databaseDTO.getConnectInfo(), DBConnectInfo.class); // 反序列化连接信息
            databaseDTO.setInfo(info); // 设置结构化信息
        }
        return databaseMapper.getDatabaseList(environmentId); // 返回列表
    }

}

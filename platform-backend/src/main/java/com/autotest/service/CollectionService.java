package com.autotest.service;

import com.autotest.common.exception.LMException;
import com.autotest.domain.Collection;
import com.autotest.domain.CollectionCase;
import com.autotest.domain.Device;
import com.autotest.mapper.CollectionCaseMapper;
import com.autotest.mapper.CollectionMapper;
import com.autotest.mapper.DeviceMapper;
import com.autotest.dto.CollectionCaseDTO;
import com.autotest.dto.CollectionDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.*;

/**
 * 服务：集合管理
 * 
 *     职责简述：提供集合的保存（含用例与设备校验）、类型查询、删除、详情与列表
 *     高频功能：
 *         1) 保存集合（校验系统类型与设备匹配，刷新集合-用例关联）
 *         2) 查询集合包含的用例类型（android/apple/环境需求）
 *         3) 分页列表查询（条件模糊处理）
 * 
 *     示例片段（入口与调用）：
 *         saveCollection(dto) -> collectionMapper.addCollection(dto);
 *         getCollectionList(req) -> collectionMapper.getCollectionList(req)
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class CollectionService {

    @Resource
    private CollectionMapper collectionMapper;

    @Resource
    private CollectionCaseMapper collectionCaseMapper;

    @Resource
    private DeviceMapper deviceMapper;

    /**
     * 保存集合（新增或更新）
     * 
     *     功能：处理集合下用例，校验系统类型与设备匹配，维护集合基础信息与用例关联
     * 
     *     @param collectionDTO // 集合DTO（含集合基础信息与用例列表）
     *     @return void         // 无返回
     * 
     *     数据示例（collectionCases）：
     *         [ { caseId:"xxx", index:1, caseSystem:"android" }, { caseId:"yyy", index:2, caseSystem:null } ]
     */
    public void saveCollection(CollectionDTO collectionDTO) {

        // 标识是否有系统用例（android/apple）
        boolean hasAndroidCase = false;
        boolean hasAppleCase = false;

        // 遍历用例列表，收集collection_case_list
        List<CollectionCase> collectionCases = new ArrayList<>();
        for(CollectionCaseDTO collectionCaseDTO: collectionDTO.getCollectionCases()){
            if("android".equals(collectionCaseDTO.getCaseSystem())){
                hasAndroidCase = true;
            }
            if("apple".equals(collectionCaseDTO.getCaseSystem())){
                hasAppleCase = true;
            }
            CollectionCase collectionCase = new CollectionCase();
            collectionCase.setId(UUID.randomUUID().toString()); // 生成集合用例主键
            collectionCase.setIndex(collectionCaseDTO.getIndex()); // 记录执行顺序
            collectionCase.setCaseId(collectionCaseDTO.getCaseId()); // 绑定用例ID
            collectionCases.add(collectionCase);
        }

        // 异常情况（Android/Apple）
        if(hasAndroidCase & hasAppleCase){
            throw new LMException("同一集合不能同时选择不同系统的测试用例");
        }
        if(hasAndroidCase || hasAppleCase){
            if(collectionDTO.getDeviceId() == null || collectionDTO.getDeviceId().equals("")){
                throw new LMException("集合下若包含APP测试则执行设备必选");
            }
            Device device = deviceMapper.getDeviceById(collectionDTO.getDeviceId());
            if(hasAndroidCase && !device.getSystem().equals("android")){
                throw new LMException("所选设备系统与集合下的测试用例类型不匹配");
            }
            if(hasAppleCase && !device.getSystem().equals("apple")){
                throw new LMException("所选设备系统与集合下的测试用例类型不匹配");
            }
        }

        // 新增 || 修改（collection）
        if(collectionDTO.getId().equals("") || collectionDTO.getId() == null){ // 新增集合
            collectionDTO.setId(UUID.randomUUID().toString()); // 生成集合主键
            collectionDTO.setCreateTime(System.currentTimeMillis()); // 记录创建时间
            collectionDTO.setUpdateTime(System.currentTimeMillis()); // 记录更新时间
            collectionDTO.setCreateUser(collectionDTO.getUpdateUser()); // 初始化创建人
            collectionMapper.addCollection(collectionDTO);
        }else{ // 修改集合
            collectionDTO.setUpdateTime(System.currentTimeMillis()); // 刷新更新时间
            collectionMapper.updateCollection(collectionDTO);
        }

        // 刷新集合-用例关联的集合ID
        collectionCases.forEach(item -> {
            item.setCollectionId(collectionDTO.getId()); // 绑定集合ID
        });

        // 清空旧的collection_case,批量新增所有的collection_case(附加collection_id)
        collectionCaseMapper.deleteCollectionCase(collectionDTO.getId());  // 先删除全部集合用例
        if(collectionCases.size() > 0) {
            collectionCaseMapper.addCollectionCase(collectionCases); // 批量新增关联
        }
    }

    /**
     * 查询集合包含的用例系统类型
     * 
     *     功能：返回集合是否包含 android/apple 用例以及是否需要环境
     * 
     *     @param collectionId // 集合ID
     *     @return Map<String, Boolean> // {hasAndroid, hasApple, needEnvironment}
     */
    public Map<String, Boolean> getCollectionCaseTypes(String collectionId){
        List<String> caseTypes = collectionCaseMapper.getCollectionCaseTypes(collectionId);
        Map<String, Boolean> caseTypeMap= new HashMap<>();
        if(caseTypes.contains("android")){
            caseTypeMap.put("hasAndroid", true);
        }else {
            caseTypeMap.put("hasAndroid", false);
        }
        if(caseTypes.contains("apple")){
            caseTypeMap.put("hasApple", true);
        }else {
            caseTypeMap.put("hasApple", false);
        }
        if(caseTypes.contains(null)){
            caseTypeMap.put("needEnvironment", true);
        }else {
            caseTypeMap.put("needEnvironment", false);
        }
        return caseTypeMap;
    }

    /**
     * 删除集合（逻辑删除）
     * 
     *     @param collection // 集合实体（仅使用id）
     *     @return void      // 无返回
     */
    public void deleteCollection(Collection collection) {
        collectionMapper.deleteCollection(collection.getId());
    }

    /**
     * 获取集合详情
     * 
     *     @param collectionId     // 集合ID
     *     @return CollectionDTO   // 集合扩展DTO（含集合下用例列表）
     */
    public CollectionDTO getCollectionDetail(String collectionId) {
        CollectionDTO collectionDTO = collectionMapper.getCollectionDetail(collectionId);
        List<CollectionCaseDTO> collectionCaseDTOS = collectionCaseMapper.getCollectionCaseList(collectionId);
        collectionDTO.setCollectionCases(collectionCaseDTOS);

        return collectionDTO;
    }

    /**
     * 分页查询集合列表
     * 
     *     功能：对模糊条件进行包装（like），返回集合扩展DTO列表
     * 
     *     @param request                 // 查询请求（项目ID+模糊条件）
     *     @return List<CollectionDTO>    // 集合扩展DTO列表
     */
    public List<CollectionDTO> getCollectionList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%"); // 包装模糊查询条件
        }
        return collectionMapper.getCollectionList(request);
    }
}

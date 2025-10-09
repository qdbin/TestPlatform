package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.dto.CollectionDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.CollectionService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;


/**
 * 控制器：集合管理
 * 
 *     职责简述：提供集合保存、类型查询、删除、详情与分页列表的HTTP入口。
 *     入参与返回遵循Service契约，进行轻量参数拼装与透传。
 */
@RestController
@RequestMapping("/autotest/collection")
public class CollectionController {

    @Resource
    private CollectionService collectionService;

    /**
     * 保存集合（新增或更新）
     * 
     *     @param collectionDTO // 集合DTO（含集合基础信息与用例列表）
     *     @param request       // 请求对象（用于获取当前用户）
     *     @return void         // 无返回
     */
    @PostMapping("/save")
    public void saveCollection(@RequestBody CollectionDTO collectionDTO, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        collectionDTO.setUpdateUser(user);
        collectionService.saveCollection(collectionDTO);
    }

    /**
     * 删除集合（逻辑删除）
     * 
     *     @param collectionDTO // 集合DTO（仅使用id）
     *     @return void         // 无返回
     */
    @PostMapping("/delete")
    public void deleteCollection(@RequestBody CollectionDTO collectionDTO) {
        collectionService.deleteCollection(collectionDTO);
    }

    /**
     * 获取集合详情
     * 
     *     @param collectionId   // 集合ID
     *     @return CollectionDTO // 集合扩展DTO（含集合下用例列表）
     */
    @GetMapping("/detail/{collectionId}")
    public CollectionDTO getCollectionDetail(@PathVariable String collectionId){
        return collectionService.getCollectionDetail(collectionId);
    }

    /**
     * 查询集合包含的用例系统类型
     * 
     *     @param collectionId            // 集合ID
     *     @return Map<String, Boolean>   // {hasAndroid, hasApple, needEnvironment}
     */
    @GetMapping("/types/{collectionId}")
    public Map<String, Boolean> getCollectionCaseTypes(@PathVariable String collectionId){
        return collectionService.getCollectionCaseTypes(collectionId);
    }

    /**
     * 分页查询集合列表
     * 
     *     @param goPage                  // 页码
     *     @param pageSize                // 页大小
     *     @param request                 // 查询请求（项目ID+模糊条件）
     *     @return Pager<List<CollectionDTO>> // 分页结果
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<CollectionDTO>> getCollectionList(@PathVariable int goPage, @PathVariable int pageSize,
                                           @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, collectionService.getCollectionList(request));
    }
}

package com.autotest.service;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.autotest.common.exception.LMException;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.dto.*;
import com.autotest.request.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * 服务：用例管理
 * 
 *     职责简述：提供用例的保存（含步骤与自定义元素/控件处理）、删除、系统类型查询、详情与列表
 *     高频功能：
 *         1) 保存用例（区分API/WEB/App步骤，支持自定义元素/控件落库与回写）
 *         2) 查询详情时回填最新UI元素/控件属性
 *         3) 分页列表查询（模糊条件包装）
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class CaseService {

    @Resource
    private CaseMapper caseMapper;

    @Resource
    private CaseApiMapper caseApiMapper;

    @Resource
    private CaseWebMapper caseWebMapper;

    @Resource
    private CaseAppMapper caseAppMapper;

    @Resource
    private ElementMapper elementMapper;

    @Resource
    private ControlMapper controlMapper;

    /**
     * 保存用例（新增或更新），并维护对应步骤
     * 
     *     功能：
     *       - 新增/更新用例基础信息（时间、用户、状态）
     *       - 依据类型处理步骤：API/WEB/App
     *       - WEB：自定义元素新增与ID回写；App：自定义控件新增与ID回写
     * 
     *     @param caseRequest // 用例请求（含基础信息与分类型步骤）
     *     @return void       // 无返回
     */
    public void saveCase(CaseRequest caseRequest) {
        // 序列化&反序列化
        JSONObject caseObject = (JSONObject) JSON.toJSON(caseRequest);
        Case testCase = caseObject.toJavaObject(Case.class);

        // 新增用例 || 更新用例
        if(testCase.getId().equals("") || testCase.getId() == null){ // 新增用例
            testCase.setId(UUID.randomUUID().toString());           // 生成主键
            testCase.setCreateTime(System.currentTimeMillis());     // 记录创建时间
            testCase.setUpdateTime(System.currentTimeMillis());     // 记录更新时间
            testCase.setCreateUser(testCase.getUpdateUser());       // 初始化创建人
            testCase.setStatus("Normal");                          // 初始化状态
            caseMapper.addCase(testCase);
        }else{ // 修改用例
            testCase.setUpdateTime(System.currentTimeMillis());     // 刷新更新时间
            caseMapper.updateCase(testCase);
        }

        // 新增API用例（按类型处理步骤，先清空旧步骤后批量新增）
        if(caseRequest.getType().equals("API")){
            // 先删除该用例相关的所有api接口（更加caseId删除所有的case_api）
            caseApiMapper.deleteCaseApi(testCase.getId());
            // 遍历对应用例的所有api接口，把json对象转为java对象
            List<CaseApiRequest> caseApiArray = caseRequest.getCaseApis();
            List<CaseApi> caseApis = new ArrayList<>();
            for(CaseApiRequest caseApiRequest: caseApiArray){
                // 序列化 & 反序列化
                JSONObject caseApiObject = (JSONObject) JSON.toJSON(caseApiRequest);
                CaseApi caseApi = caseApiObject.toJavaObject(CaseApi.class);
                caseApi.setCaseId(testCase.getId());                 // 绑定用例ID
                caseApi.setId(UUID.randomUUID().toString());         // 生成步骤主键
                caseApis.add(caseApi);
            }
            caseApiMapper.addCaseApi(caseApis);
        }

        // 新增web操作步骤
        else if (caseRequest.getType().equals("WEB")){ 
            caseWebMapper.deleteCaseWeb(testCase.getId());  // 先删除全部用例接口
            List<CaseWebRequest> caseWebArray = caseRequest.getCaseWebs();
            List<CaseWeb> caseWebs = new ArrayList<>();
            for(CaseWebRequest caseWebRequest: caseWebArray){
                String operationId = caseWebRequest.getOperationId();
                JSONArray elements = caseWebRequest.getElement();
                // 关键步骤：处理自定义元素并落库，随后将ID回写到步骤中
                for(int i=0;i<elements.size();i++){
                    JSONObject element = elements.getJSONObject(i);
                    if(element.getBoolean("custom")){
                        Element ele = new Element();
                        ele.setId(UUID.randomUUID().toString());
                        ele.setName(element.getString("name"));
                        ele.setBy(element.getString("by"));
                        ele.setExpression(element.getString("expression"));
                        ele.setModuleId(element.getString("moduleId"));
                        ele.setProjectId(testCase.getProjectId());
                        ele.setCreateTime(System.currentTimeMillis());
                        ele.setUpdateTime(System.currentTimeMillis());
                        ele.setCreateUser(testCase.getUpdateUser());
                        ele.setUpdateUser(testCase.getUpdateUser());
                        ele.setStatus("Normal");
                        try {
                            elementMapper.addElement(ele);
                        }catch (Exception e){
                            throw new LMException("自定义的元素新增失败 请检查命名是否重复");
                        }
                        // 回写元素
                        element.put("id", ele.getId());
                        element.put("custom", false);
                    }
                }
                JSONObject caseWebObject = (JSONObject) JSON.toJSON(caseWebRequest);
                CaseWeb caseWeb = caseWebObject.toJavaObject(CaseWeb.class);
                caseWeb.setOperationId(operationId);
                caseWeb.setCaseId(testCase.getId());                 // 绑定用例ID
                caseWeb.setId(UUID.randomUUID().toString());         // 生成步骤主键
                caseWebs.add(caseWeb);
            }
            caseWebMapper.addCaseWeb(caseWebs);
        }

        // 新增app操作步骤
        else { 
            caseAppMapper.deleteCaseApp(testCase.getId());  // 先删除全部用例接口
            List<CaseAppRequest> caseAppArray = caseRequest.getCaseApps();
            List<CaseApp> caseApps = new ArrayList<>();
            for(CaseAppRequest caseAppRequest: caseAppArray){
                String operationId = caseAppRequest.getOperationId();
                JSONArray controls = caseAppRequest.getElement();
                // 关键步骤：处理自定义控件并落库，随后将ID回写到步骤中
                for(int i=0;i<controls.size();i++){
                    JSONObject control = controls.getJSONObject(i);
                    if(control.getBoolean("custom")){
                        Control con = new Control();
                        con.setId(UUID.randomUUID().toString());
                        con.setName(control.getString("name"));
                        con.setSystem(control.getString("system"));
                        con.setBy(control.getString("by"));
                        con.setExpression(control.getString("expression"));
                        con.setModuleId(control.getString("moduleId"));
                        con.setProjectId(testCase.getProjectId());
                        con.setCreateTime(System.currentTimeMillis());
                        con.setUpdateTime(System.currentTimeMillis());
                        con.setCreateUser(testCase.getUpdateUser());
                        con.setUpdateUser(testCase.getUpdateUser());
                        con.setStatus("Normal");
                        try {
                            controlMapper.addControl(con);
                        }catch (Exception e){
                            throw new LMException("自定义的控件新增失败 请检查命名是否重复");
                        }
                        // 回写元素
                        control.put("id", con.getId());
                        control.put("custom", false);
                    }
                }
                JSONObject caseAppObject = (JSONObject) JSON.toJSON(caseAppRequest);
                CaseApp caseApp = caseAppObject.toJavaObject(CaseApp.class);
                caseApp.setOperationId(operationId);
                caseApp.setCaseId(testCase.getId());                 // 绑定用例ID
                caseApp.setId(UUID.randomUUID().toString());         // 生成步骤主键
                caseApps.add(caseApp);
            }
            caseAppMapper.addCaseApp(caseApps);
        }
    }

    /**
     * 删除用例（逻辑删除）
     * 
     *     @param caseRequest // 用例请求（仅使用id）
     *     @return void       // 无返回
     */
    public void deleteCase(CaseRequest caseRequest) {
        caseMapper.deleteCase(caseRequest.getId());
    }

    /**
     * 查询用例系统类型
     * 
     *     @param caseId   // 用例ID
     *     @return String  // 系统类型（web/app/android/apple等）
     */
    public String getCaseSystem(String caseId){
        return caseMapper.getCaseSystem(caseId);
    }

    /**
     * 获取用例详情（按类型回填步骤与最新UI属性）
     * 
     *     @param caseType   // 用例类型（API/WEB/android/apple）
     *     @param caseId     // 用例ID
     *     @return CaseDTO   // 用例扩展DTO（含步骤列表）
     */
    public CaseDTO getCaseDetail(String caseType, String caseId) {
        CaseDTO caseDTO = caseMapper.getCaseDetail(caseId);
        // API
        if(caseType.equalsIgnoreCase("API")){
            List<CaseApiDTO> caseApis = caseApiMapper.getCaseApiList(caseId);
            caseDTO.setCaseApis(caseApis);
        }

        // WEB
        else if(caseType.equalsIgnoreCase("WEB")){
            List<CaseWebDTO> caseWebs = caseWebMapper.getCaseWebList(caseId, caseType.toLowerCase(Locale.ROOT));
            // 加载最新的UI元素
            for(CaseWebDTO caseWebDTO:caseWebs){
                JSONArray elementList = JSONArray.parseArray(caseWebDTO.getElement());
                for(int i=0;i<elementList.size();i++){
                    JSONObject element = elementList.getJSONObject(i);
                    String elementId = element.getString("id");
                    if(elementId == null || elementId.equals("")){
                        continue;
                    }
                    ElementDTO elementDTO = elementMapper.getElementById(elementId);
                    element.put("by", elementDTO.getBy());
                    element.put("name", elementDTO.getName());
                    element.put("expression", elementDTO.getExpression());
                    element.put("moduleId", elementDTO.getModuleId());
                    element.put("moduleName", elementDTO.getModuleName());
                }
                caseWebDTO.setElement(JSONArray.toJSONString(elementList));
            }
            caseDTO.setCaseWebs(caseWebs);
        }

        // APP
        else {
            List<CaseAppDTO> caseApps = caseAppMapper.getCaseAppList(caseId, caseType.toLowerCase(Locale.ROOT));
            // 加载最新的UI元素
            for(CaseAppDTO caseAppDTO:caseApps){
                JSONArray controlList = JSONArray.parseArray(caseAppDTO.getElement());
                for(int i=0;i<controlList.size();i++){
                    JSONObject control = controlList.getJSONObject(i);
                    String controlId = control.getString("id");
                    if(controlId == null || controlId.equals("")){
                        continue;
                    }
                    ControlDTO controlDTO = controlMapper.getControlById(controlId);
                    control.put("system", controlDTO.getSystem());
                    control.put("by", controlDTO.getBy());
                    control.put("name", controlDTO.getName());
                    control.put("expression", controlDTO.getExpression());
                    control.put("moduleId", controlDTO.getModuleId());
                    control.put("moduleName", controlDTO.getModuleName());
                }
                caseAppDTO.setElement(JSONArray.toJSONString(controlList));
            }
            caseDTO.setCaseApps(caseApps);
        }

        return caseDTO;
    }

    /**
     * 分页查询用例列表
     * 
     *     功能：对模糊条件进行包装（like），返回用例扩展DTO列表
     * 
     *     @param request              // 查询请求（项目ID+模糊条件等）
     *     @return List<CaseDTO>       // 用例扩展DTO列表
     */
    public List<CaseDTO> getCaseList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%"); // 包装模糊Query条件
        }
        return caseMapper.getCaseList(request);
    }
}

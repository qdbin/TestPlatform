package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.parser.Feature;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.autotest.common.constants.DeviceStatus;
import com.autotest.common.constants.ReportSourceType;
import com.autotest.common.exception.LMException;
import com.autotest.common.utils.FileUtils;
import com.autotest.common.utils.ZipUtils;
import com.autotest.domain.*;
import com.autotest.mapper.*;
import com.autotest.dto.*;
import com.autotest.request.CaseApiRequest;
import com.autotest.request.CaseAppRequest;
import com.autotest.request.CaseRequest;
import com.autotest.request.CaseWebRequest;
import com.autotest.response.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * 用例JSON构建服务：生成与整理（key:value）
 *
 * 介绍: 根据任务与集合数据，统一构建 API/WEB/APP 用例的 JSON 数据，并负责压缩打包生成下载链接；同时提供用例调试数据的快速生成。
 * 高频功能: 构建三类用例数据；合并公参与控制器配置；生成下载地址。
 * 使用示例: getDownloadUrl(task, list) -> 内部按类型调用 getApiTestCaseJson/getWebTestCaseJson/getAppTestCaseJson 生成文件。
 */
@Service
public class CaseJsonCreateService {

    @Value("${task.file.path}")
    public String TASK_FILE_PATH; // 任务文件根路径

    private static final String DOWNLOAD_PATH = "/openapi/task/file/download"; // 下载接口相对路径

    @Resource
    private EngineMapper engineMapper; // 引擎信息访问

    @Resource
    private CaseMapper caseMapper; // 用例基本信息访问

    @Resource
    private ApiMapper apiMapper; // 接口信息访问

    @Resource
    private CaseApiMapper caseApiMapper; // API用例步骤访问

    @Resource
    private CaseWebMapper caseWebMapper; // WEB用例步骤访问

    @Resource
    private CaseAppMapper caseAppMapper; // APP用例步骤访问

    @Resource
    private CollectionMapper collectionMapper; // 集合信息访问

    @Resource
    private DebugDataMapper debugDataMapper; // 调试数据访问

    @Resource
    private PlanCollectionMapper planCollectionMapper; // 计划-集合关系访问

    @Resource
    private CollectionCaseMapper collectionCaseMapper; // 集合-用例关系访问

    @Resource
    private DomainMapper domainMapper; // 域名配置访问

    @Resource
    private CommonParamMapper commonParamMapper; // 公参配置访问

    @Resource
    private OperationMapper operationMapper; // 操作定义访问

    @Resource
    private FunctionMapper functionMapper; // 自定义函数访问

    @Resource
    private TaskMapper taskMapper; // 任务信息访问

    @Resource
    private ElementMapper elementMapper; // 元素定义访问

    @Resource
    private ControlMapper controlMapper; // 控制器配置访问

    @Resource
    private DeviceMapper deviceMapper; // 设备信息访问

    @Resource
    private ApplicationMapper applicationMapper; // 应用信息访问

    @Resource
    private DriverMapper driverMapper; // 浏览器驱动配置访问

    @Resource
    private DatabaseMapper databaseMapper; // 数据库配置访问

    /**
     * 生成下载链接（函数功能）
     *
     * @param task                 // 任务上下文，含环境、来源、项目等标识
     * @param testCollectionList   // 测试集合-用例列表，用于生成对应 JSON 文件
     * @return String              // 压缩包下载路径（相对路径）
     *
     * 示例: 入参(task, collections) -> 调用本方法循环写入 JSON -> 返回 "/openapi/task/file/download/{taskId}"。
     */
    public String getDownloadUrl(TaskDTO task, List<TaskTestCollectionResponse> testCollectionList){
        String taskFilePath = TASK_FILE_PATH+"/"+task.getProjectId()+"/"+task.getId();
        String taskZipPath = TASK_FILE_PATH+"/"+task.getProjectId();
        String zipFileName = task.getId();
        for(TaskTestCollectionResponse taskTestCollection: testCollectionList){
            String collectionFilePath = taskFilePath +"/"+ taskTestCollection.getCollectionId();
            for(TaskTestCaseResponse taskTestCase:taskTestCollection.getTestCaseList()){
                if(taskTestCase.getCaseType().equals("API")) {
                    // 生成 API 用例 JSON
                    TestCaseApiResponse testCase = this.getApiTestCaseJson(task.getEnvironmentId(), task.getSourceType(), taskTestCase);
                    JSONObject taskCase = JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
                    // 同一个集合下同一条用例文件重复就覆盖 因数据一样没必要生成两份
                    FileUtils.createJsonFile(taskCase, collectionFilePath + "/" + testCase.getCaseId() + ".json");
                }else if(taskTestCase.getCaseType().equals("WEB")){ // WEB用例
                    // 生成 WEB 用例 JSON
                    TestCaseWebResponse testCase = this.getWebTestCaseJson(task.getEnvironmentId(),task.getSourceType(), taskTestCase);
                    JSONObject taskCase = JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
                    // 同一个集合下同一条用例文件重复就覆盖 因数据一样没必要生成两份
                    FileUtils.createJsonFile(taskCase, collectionFilePath + "/" + testCase.getCaseId() + ".json");
                }else { // APP用例
                    // 生成 APP 用例 JSON
                    TestCaseAppResponse testCase = this.getAppTestCaseJson(taskTestCollection.getDeviceId(), task.getSourceType(), taskTestCase);
                    JSONObject taskCase = JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
                    // 同一个集合下同一条用例文件重复就覆盖 因数据一样没必要生成两份
                    FileUtils.createJsonFile(taskCase, collectionFilePath + "/" + testCase.getCaseId() + ".json");
                }
            }
        }
        try { // 打包文件
            ZipUtils.compress(taskFilePath, taskZipPath, zipFileName);
            // 打包完成删除源文件夹
            FileUtils.deleteDir(taskFilePath);
            return DOWNLOAD_PATH+"/"+task.getId();
        } catch (Exception exception) {
            throw new LMException("json文件压缩失败");
        }
    }

    /**
     * 获取调试数据（函数功能）
     *
     * @param task
     * @param testCollectionList
     * @return JSONObject
     */
    public JSONObject getDebugData(TaskDTO task, List<TaskTestCollectionResponse> testCollectionList){
        // case
        TaskTestCaseResponse taskTestCase = testCollectionList.get(0).getTestCaseList().get(0);

        // api
        if(taskTestCase.getCaseType().equals("API")){
            TestCaseApiResponse testCase = this.getApiTestCaseJson(task.getEnvironmentId(),task.getSourceType(), taskTestCase);
            // WriteMapNullValue: 忽略值为null的字段 || OrderedField: 严格给定顺序排列
            return JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
        }

        // web
        else if(taskTestCase.getCaseType().equals("WEB")){ // web用例
            TestCaseWebResponse testCase = this.getWebTestCaseJson(task.getEnvironmentId(),task.getSourceType(), taskTestCase);
            return JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
        }
        // app
        else { // app用例
            TestCaseAppResponse testCase = this.getAppTestCaseJson(testCollectionList.get(0).getDeviceId(),task.getSourceType(), taskTestCase);
            return JSONObject.parseObject(JSONObject.toJSONString(testCase, SerializerFeature.WriteMapNullValue), Feature.OrderedField);
        }
    }

    /**
     * 生成 APP 用例 JSON（函数功能）
     *
     * @param deviceId     // 设备标识，用于填充设备信息
     * @param SourceType   // 来源类型：PLAN/COLLECTION/CASE/TEMP
     * @param taskTestCase // 测试用例索引信息
     * @return TestCaseAppResponse // APP 用例数据结构
     *
     * 示例: 入参包含临时调试或正式用例 -> 依来源装配函数、公参、应用与设备信息 -> 返回包含操作列表的 APP 用例。
     */
    public TestCaseAppResponse getAppTestCaseJson(String deviceId, String SourceType, TaskTestCaseResponse taskTestCase){
        // 拼装App用例
        TestCaseAppResponse testCaseApp = new TestCaseAppResponse();
        if(SourceType.equals(ReportSourceType.TEMP.toString())) {
            // 调试场景：读取临时数据
            DebugData debugData = debugDataMapper.getDebugData(taskTestCase.getCaseId());
            CaseRequest caseRequest = JSONObject.parseObject(debugData.getData(), CaseRequest.class);
            testCaseApp.setComment(caseRequest.getDescription());
            testCaseApp.setCaseId(taskTestCase.getCaseId());
            testCaseApp.setCaseName(caseRequest.getName());
            // 组装自定义函数
            testCaseApp.setFunctions(this.getCaseFunctions(caseRequest.getCommonParam().getJSONArray("functions")));
            // 组装用例公参
            testCaseApp.setParams(this.getCaseParams(caseRequest.getCommonParam().getJSONArray("params")));
            // 组装应用信息
            Application application = applicationMapper.getApplicationById(caseRequest.getCommonParam().getString("appId"));
            testCaseApp.setAppId(application.getAppId());
            if(caseRequest.getCommonParam().getString("activity")!=null &&
                    !caseRequest.getCommonParam().getString("activity").equals("")){
                testCaseApp.setActivity(caseRequest.getCommonParam().getString("activity"));
            }else {
                testCaseApp.setActivity(application.getMainActivity());
            }
            // 组装设备信息
            Device device = deviceMapper.getDeviceById(deviceId);
            testCaseApp.setDeviceSystem(device.getSystem());
            if(device.getSystem().equals("android")) {
                testCaseApp.setDeviceUrl(JSONObject.parseObject(device.getSources()).getString("atxAgentAddress")); // Android 设备控制端地址
            }else {
                testCaseApp.setDeviceUrl(JSONObject.parseObject(device.getSources()).getString("wdaUrl")); // iOS 设备控制端地址
            }
            // 组装操作
            List<CaseAppRequest> caseApps = caseRequest.getCaseApps();
            List<TestCaseAppDataResponse> optList = new ArrayList<>();
            for (CaseAppRequest caseAppRequest:caseApps){
                TestCaseAppDataResponse optData = new TestCaseAppDataResponse();
                Operation operation = operationMapper.getOperationDetail(caseAppRequest.getOperationId(), caseRequest.getType().toLowerCase(Locale.ROOT));
                optData.setOperationType(operation.getType());
                optData.setOperationSystem(caseRequest.getSystem());
                optData.setOperationId(caseAppRequest.getOperationId());
                if(operation.getFrom().equals("custom")){
                    optData.setOperationName("自定义");
                    optData.setOperationCode(operation.getCode());
                }else {
                    optData.setOperationName(operation.getName());
                    optData.setOperationCode(null);
                }
                optData.setOperationDesc(caseAppRequest.getDescription());
                optData.setOperationTrans(operation.getName());
                optData.setOperationElement(this.getAppElement(caseAppRequest.getElement()));
                optData.setOperationData(this.getAppData(caseAppRequest.getData()));
                optList.add(optData);
            }
            testCaseApp.setOptList(optList);
        }else {
            CaseDTO caseDTO = caseMapper.getCaseDetail(taskTestCase.getCaseId());
            testCaseApp.setComment(caseDTO.getDescription());
            testCaseApp.setCaseId(taskTestCase.getCaseId());
            testCaseApp.setCaseName(caseDTO.getName());
            JSONObject commonParam = JSONObject.parseObject(caseDTO.getCommonParam());
            // 组装自定义函数
            testCaseApp.setFunctions(this.getCaseFunctions(commonParam.getJSONArray("functions")));
            // 组装用例公参
            testCaseApp.setParams(this.getCaseParams(commonParam.getJSONArray("params")));
            // 组装应用信息
            Application application = applicationMapper.getApplicationById(commonParam.getString("appId"));
            testCaseApp.setAppId(application.getAppId());
            if(commonParam.getString("activity")!=null &&
                    !commonParam.getString("activity").equals("")){
                testCaseApp.setActivity(commonParam.getString("activity"));
            }else {
                testCaseApp.setActivity(application.getMainActivity());
            }
            // 组装设备信息
            if(deviceId != null) {  // 测试集合或测试计划执行时设备可能不在线 无法执行 将在引擎返回的执行日志中提示
                Device device = deviceMapper.getDeviceById(deviceId);
                testCaseApp.setDeviceSystem(device.getSystem());
                if (device.getSystem().equals("android")) {
                    testCaseApp.setDeviceUrl(JSONObject.parseObject(device.getSources()).getString("atxAgentAddress"));
                } else {
                    testCaseApp.setDeviceUrl(JSONObject.parseObject(device.getSources()).getString("wdaUrl"));
                }
            }
            // 组装操作
            List<CaseAppDTO> caseApps = caseAppMapper.getCaseAppList(taskTestCase.getCaseId(), taskTestCase.getCaseType().toLowerCase(Locale.ROOT));
            List<TestCaseAppDataResponse> optList = new ArrayList<>();
            for (CaseAppDTO caseAppDTO:caseApps){
                TestCaseAppDataResponse optData = new TestCaseAppDataResponse();
                Operation operation = operationMapper.getOperationDetail(caseAppDTO.getOperationId(), caseDTO.getType().toLowerCase(Locale.ROOT));
                optData.setOperationType(operation.getType());
                optData.setOperationSystem(caseDTO.getSystem());
                optData.setOperationId(caseAppDTO.getOperationId());
                if(operation.getFrom().equals("custom")){
                    optData.setOperationName("自定义");
                    optData.setOperationCode(operation.getCode());
                }else {
                    optData.setOperationName(operation.getName());
                    optData.setOperationCode(null);
                }
                optData.setOperationDesc(caseAppDTO.getDescription());
                optData.setOperationTrans(operation.getName());
                optData.setOperationElement(this.getAppElement(JSONArray.parseArray(caseAppDTO.getElement())));
                optData.setOperationData(this.getAppData(JSONArray.parseArray(caseAppDTO.getData())));
                optList.add(optData);
            }
            testCaseApp.setOptList(optList);
        }
        return testCaseApp;
    }

    /**
     * 构建WEB用例JSON（函数功能）
     *
     * @param environmentId // 环境ID，用于域名、数据库解析
     * @param SourceType    // 来源类型：PLAN/COLLECTION/CASE/TEMP
     * @param taskTestCase  // 用例索引信息（集合/计划中的用例）
     * @return TestCaseWebResponse // WEB用例数据结构
     *
     * 示例：入参(taskTestCase) -> 按来源读取操作/元素/数据 -> 返回WEB用例JSON
     */
    public TestCaseWebResponse getWebTestCaseJson(String environmentId, String SourceType, TaskTestCaseResponse taskTestCase){
        // 拼装Web用例
        TestCaseWebResponse testCaseWeb = new TestCaseWebResponse();
        if(SourceType.equals(ReportSourceType.TEMP.toString())) {
            DebugData debugData = debugDataMapper.getDebugData(taskTestCase.getCaseId());
            CaseRequest caseRequest = JSONObject.parseObject(debugData.getData(), CaseRequest.class);
            testCaseWeb.setComment(caseRequest.getDescription());
            testCaseWeb.setCaseId(taskTestCase.getCaseId());
            testCaseWeb.setCaseName(caseRequest.getName());
            // 组装自定义函数
            testCaseWeb.setFunctions(this.getCaseFunctions(caseRequest.getCommonParam().getJSONArray("functions")));
            // 组装用例公参
            testCaseWeb.setParams(this.getCaseParams(caseRequest.getCommonParam().getJSONArray("params")));
            // 组装浏览器开关配置
            testCaseWeb.setStartDriver(caseRequest.getCommonParam().getBoolean("startDriver"));
            testCaseWeb.setCloseDriver(caseRequest.getCommonParam().getBoolean("closeDriver"));
            // 组装浏览器driver配置
            testCaseWeb.setDriverSetting(this.getDriverSetting(caseRequest.getCommonParam()));
            // 组装操作
            List<CaseWebRequest> caseWebs = caseRequest.getCaseWebs();
            List<TestCaseWebDataResponse> optList = new ArrayList<>();
            for (CaseWebRequest caseWebRequest:caseWebs){
                TestCaseWebDataResponse optData = new TestCaseWebDataResponse();
                Operation operation = operationMapper.getOperationDetail(caseWebRequest.getOperationId(), caseRequest.getType().toLowerCase(Locale.ROOT));
                optData.setOperationType(operation.getType());
                optData.setOperationId(caseWebRequest.getOperationId());
                if(operation.getFrom().equals("custom")){
                    optData.setOperationName("自定义");
                    optData.setOperationCode(operation.getCode());
                }else {
                    optData.setOperationName(operation.getName());
                    optData.setOperationCode(null);
                }
                optData.setOperationDesc(caseWebRequest.getDescription());
                optData.setOperationTrans(operation.getName());
                optData.setOperationElement(this.getWebElement(caseWebRequest.getElement()));
                optData.setOperationData(this.getWebData(caseWebRequest.getData(), environmentId));
                optList.add(optData);
            }
            testCaseWeb.setOptList(optList);
        }else {
            CaseDTO caseDTO = caseMapper.getCaseDetail(taskTestCase.getCaseId());
            testCaseWeb.setComment(caseDTO.getDescription());
            testCaseWeb.setCaseId(taskTestCase.getCaseId());
            testCaseWeb.setCaseName(caseDTO.getName());
            JSONObject commonParam = JSONObject.parseObject(caseDTO.getCommonParam());
            // 组装自定义函数
            testCaseWeb.setFunctions(this.getCaseFunctions(commonParam.getJSONArray("functions")));
            // 组装用例公参
            testCaseWeb.setParams(this.getCaseParams(commonParam.getJSONArray("params")));
            // 组装浏览器开关配置
            testCaseWeb.setStartDriver(commonParam.getBoolean("startDriver"));
            testCaseWeb.setCloseDriver(commonParam.getBoolean("closeDriver"));
            // 组装浏览器driver配置
            testCaseWeb.setDriverSetting(this.getDriverSetting(commonParam));
            // 组装操作
            List<CaseWebDTO> caseWebs = caseWebMapper.getCaseWebList(taskTestCase.getCaseId(), taskTestCase.getCaseType().toLowerCase(Locale.ROOT));
            List<TestCaseWebDataResponse> optList = new ArrayList<>();
            for (CaseWebDTO caseWebDTO:caseWebs){
                TestCaseWebDataResponse optData = new TestCaseWebDataResponse();
                Operation operation = operationMapper.getOperationDetail(caseWebDTO.getOperationId(), caseDTO.getType().toLowerCase(Locale.ROOT));
                optData.setOperationType(operation.getType());
                optData.setOperationId(caseWebDTO.getOperationId());
                if(operation.getFrom().equals("custom")){
                    optData.setOperationName("自定义");
                    optData.setOperationCode(operation.getCode());
                }else {
                    optData.setOperationName(operation.getName());
                    optData.setOperationCode(null);
                }
                optData.setOperationDesc(caseWebDTO.getDescription());
                optData.setOperationTrans(operation.getName());
                optData.setOperationElement(this.getWebElement(JSONArray.parseArray(caseWebDTO.getElement())));
                optData.setOperationData(this.getWebData(JSONArray.parseArray(caseWebDTO.getData()), environmentId));
                optList.add(optData);
            }
            testCaseWeb.setOptList(optList);
        }
        return testCaseWeb;
    }

    /**
     * 构建API用例JSON（函数功能）
     *
     * @param environmentId // 环境ID，用于域名、数据库解析
     * @param SourceType    // 来源类型：PLAN/COLLECTION/CASE/TEMP
     * @param taskTestCase  // 用例索引信息（集合/计划中的用例）
     * @return TestCaseApiResponse // API用例数据结构
     *
     * 主要思想：解析用例,数据封装
     *      1. 拿到具体case的详细信息：task的source_id是debug_data_id，获得debug_data表中的data数据，将其解析为json对象
     *      2. 将case常规数据进行赋值，查询case_api连表case,得到case的通用信息
     *      3. 对于一些字段的值是其id的，需要查询并验证无误后，再进行更新赋值（验证主要是验证是否为空，是否有效）
     *      4. 由于很多字典格式的数据，在数据库中存储的是字符串，所有拿出来要解析为Json对象，像[]或{}最终放的都是JSON对象
     */
    public TestCaseApiResponse getApiTestCaseJson(String environmentId, String SourceType, TaskTestCaseResponse taskTestCase){
        // 拼装Api用例
        TestCaseApiResponse testCaseApi = new TestCaseApiResponse();

        // tmp类型
        if(SourceType.equals(ReportSourceType.TEMP.toString())){
            // 获取debugData
            DebugData debugData = debugDataMapper.getDebugData(taskTestCase.getCaseId());
            CaseRequest caseRequest = JSONObject.parseObject(debugData.getData(), CaseRequest.class);   // 将String转为Object

            // 基本信息（caseId,name,description）
            testCaseApi.setComment(caseRequest.getDescription());
            testCaseApi.setCaseId(taskTestCase.getCaseId());
            testCaseApi.setCaseName(caseRequest.getName());

            // 组装自定义函数
            testCaseApi.setFunctions(this.getCaseFunctions(caseRequest.getCommonParam().getJSONArray("functions")));

            // 组装公参
            testCaseApi.setParams(this.getCaseParams(caseRequest.getCommonParam().getJSONArray("params")));

            // 组装apiList
            List<CaseApiRequest> caseApis = caseRequest.getCaseApis();
            List<TestCaseApiDataResponse> apiList = new ArrayList<>();
            for (CaseApiRequest caseApiRequest:caseApis){
                TestCaseApiDataResponse apiData = new TestCaseApiDataResponse();
                // 根据所属case,更新公共info（method、url、path、protocol、）
                ApiDTO apiDTO = apiMapper.getApiDetail(caseApiRequest.getApiId());
                apiData.setApiId(caseApiRequest.getApiId());    // case_api_id
                apiData.setApiName(apiDTO.getName());           // case_name
                apiData.setApiDesc(caseApiRequest.getDescription());    // case_api_desc
                apiData.setUrl(this.getUrlBySign(environmentId, apiDTO.getDomainSign(), apiDTO.getPath()));
                apiData.setPath(apiDTO.getPath());
                apiData.setMethod(apiDTO.getMethod());
                apiData.setProtocol(apiDTO.getProtocol());
                // 拼接header
                apiData.setHeaders(this.getApiHeader(caseRequest.getCommonParam().getString("header"), caseApiRequest.getHeader()));
                // 拼接proxy（根据controller字典中获得）
                apiData.setProxies(this.getApiProxy(caseRequest.getCommonParam().getString("proxy"), caseApiRequest.getController()));
                // 组装body
                apiData.setBody(caseApiRequest.getBody());
                // 组装query
                apiData.setQuery(this.getApiQuery(caseApiRequest.getQuery()));
                // 组装rest
                apiData.setRest(this.getApiRest(caseApiRequest.getRest()));
                // 组装relation assertion
                apiData.setRelations(caseApiRequest.getRelation());
                apiData.setAssertions(caseApiRequest.getAssertion());
                // 组装controller
                apiData.setController(this.getApiController(environmentId, caseApiRequest.getController()));
                apiList.add(apiData);
            }
            testCaseApi.setApiList(apiList);
        }

        // case类型
        else {
            CaseDTO caseDTO = caseMapper.getCaseDetail(taskTestCase.getCaseId());
            testCaseApi.setComment(caseDTO.getDescription());
            testCaseApi.setCaseId(taskTestCase.getCaseId());
            testCaseApi.setCaseName(caseDTO.getName());
            JSONObject commonParam = JSONObject.parseObject(caseDTO.getCommonParam());
            // 组装自定义函数
            testCaseApi.setFunctions(this.getCaseFunctions(commonParam.getJSONArray("functions")));
            // 组装用例公参
            testCaseApi.setParams(this.getCaseParams(commonParam.getJSONArray("params")));
            List<CaseApiDTO> caseApiDTOS = caseApiMapper.getCaseApiList(taskTestCase.getCaseId());
            List<TestCaseApiDataResponse> apiList = new ArrayList<>();
            for(CaseApiDTO caseApiDTO: caseApiDTOS){
                TestCaseApiDataResponse apiData = new TestCaseApiDataResponse();
                apiData.setApiId(caseApiDTO.getApiId());
                apiData.setApiName(caseApiDTO.getApiName());
                apiData.setApiDesc(caseApiDTO.getDescription());
                apiData.setUrl(this.getUrlBySign(environmentId, caseApiDTO.getApiDomainSign(), caseApiDTO.getApiPath()));   // 匹配url（若标识非空直接替换，若不是则遍历头匹配）
                apiData.setPath(caseApiDTO.getApiPath());
                apiData.setMethod(caseApiDTO.getApiMethod());
                apiData.setProtocol(caseApiDTO.getApiProtocol());
                // 拼接header
                JSONArray headers = JSONArray.parseArray(caseApiDTO.getHeader());
                apiData.setHeaders(this.getApiHeader(commonParam.getString("header"), headers));
                // 拼接proxy
                apiData.setProxies(this.getApiProxy(commonParam.getString("proxy"), JSONArray.parseArray(caseApiDTO.getController())));
                // 组装body
                apiData.setBody(JSONObject.parseObject(caseApiDTO.getBody()));
                // 组装query
                apiData.setQuery(this.getApiQuery(JSONArray.parseArray(caseApiDTO.getQuery())));
                // 组装rest
                apiData.setRest(this.getApiRest(JSONArray.parseArray(caseApiDTO.getRest())));
                // 组装relation assertion
                apiData.setRelations(JSONArray.parseArray(caseApiDTO.getRelation()));
                apiData.setAssertions(JSONArray.parseArray(caseApiDTO.getAssertion()));
                // 组装controller
                apiData.setController(this.getApiController(environmentId, JSONArray.parseArray(caseApiDTO.getController())));
                apiList.add(apiData);
            }
            testCaseApi.setApiList(apiList);
        }

        return testCaseApi;
    }

    /**
     * 构建APP元素映射
     *
     * @param elements // 元素ID列表
     * @return JSONObject // 元素详情映射{name: {定位方式/值}}
     */
    public JSONObject getAppElement(JSONArray elements){
        JSONObject elementObj = new JSONObject();
        if(elements == null){
            return elementObj;
        }
        for(int i=0;i<elements.size();i++){
            JSONObject element = elements.getJSONObject(i);
            JSONObject elementData = new JSONObject();
            // 获取最新元素
            ControlDTO controlDTO = controlMapper.getControlById(element.getString("id"));
            if(controlDTO != null) {
                elementData.put("by", controlDTO.getBy());
                elementData.put("expression", controlDTO.getExpression());
                elementData.put("target", controlDTO.getModuleName() + " / " + controlDTO.getName());
            }else {
                elementData.put("by", element.getString("by"));
                elementData.put("expression", element.getString("expression"));
                elementData.put("target", element.getString("moduleName") + " / " + element.getString("name"));
            }
            elementObj.put(element.getString("paramName"), elementData);
        }
        return elementObj;
    }

    /**
     * 构建APP数据参数
     *
     * @param dataList // 数据ID列表
     * @return JSONObject // 数据键值映射
     */
    public JSONObject getAppData(JSONArray dataList){
        JSONObject dataObj = new JSONObject();
        if(dataList == null){
            return dataObj;
        }
        for(int i=0;i<dataList.size();i++){
            JSONObject data = dataList.getJSONObject(i);
            JSONObject dataValue = new JSONObject();
            dataValue.put("type", data.getString("type"));
            dataValue.put("value", data.getString("value"));
            dataObj.put(data.getString("paramName"), dataValue);
        }
        if(dataObj.containsKey("appId")){
            String appValue = dataObj.getJSONObject("appId").getString("value");
            if(appValue != null && !appValue.equals("")){
                // 根据域名标识来获取域名
                Application application = applicationMapper.getApplicationById(appValue);
                if(application != null) {
                    dataObj.getJSONObject("appId").put("value", application.getAppId());
                }
            }
        }
        return dataObj;
    }

    /**
     * 构建Driver配置
     *
     * @param commonParam // 公参对象
     * @return JSONObject // 驱动配置（平台、设备、应用、driver）
     */
    public JSONObject getDriverSetting(JSONObject commonParam){
        if(!commonParam.containsKey("driverSetting")){
            return new JSONObject();
        }
        String driverId = commonParam.getString("driverSetting");
        Driver driver = driverMapper.getDriverById(driverId);
        if(driver == null){
            return new JSONObject();
        }
        return JSONObject.parseObject(driver.getSetting());
    }

    /**
     * 构建WEB元素映射
     *
     * @param elements // 元素ID列表
     * @return JSONObject // 元素详情映射{name: {定位方式/值}}
     */
    public JSONObject getWebElement(JSONArray elements){
        JSONObject elementObj = new JSONObject();
        if(elements == null){
            return elementObj;
        }
        for(int i=0;i<elements.size();i++){
            JSONObject element = elements.getJSONObject(i);
            JSONObject elementData = new JSONObject();
            // 获取最新元素
            ElementDTO elementDTO = elementMapper.getElementById(element.getString("id"));
            if(elementDTO != null) {
                elementData.put("by", elementDTO.getBy());
                elementData.put("expression", elementDTO.getExpression());
                elementData.put("target", elementDTO.getModuleName() + " / " + elementDTO.getName());
            }else {
                elementData.put("by", element.getString("by"));
                elementData.put("expression", element.getString("expression"));
                elementData.put("target", element.getString("moduleName") + " / " + element.getString("name"));
            }
            elementObj.put(element.getString("paramName"), elementData);
        }
        return elementObj;
    }

    /**
     * 构建WEB数据参数（支持环境变量、数据库参数）
     *
     * @param dataList       // 数据ID列表
     * @param environmentId  // 环境ID，用于解析环境变量/数据库
     * @return JSONObject    // 数据键值映射
     */
    public JSONObject getWebData(JSONArray dataList, String environmentId){
        JSONObject dataObj = new JSONObject(); // 初始化结果对象
        if(dataList == null){
            return dataObj; // 空数据直接返回
        }
        for(int i=0;i<dataList.size();i++){
            JSONObject data = dataList.getJSONObject(i); // 读取一条数据
            JSONObject dataValue = new JSONObject(); // 构造值结构
            dataValue.put("type", data.getString("type")); // 类型写入
            dataValue.put("value", data.getString("value")); // 值写入
            dataObj.put(data.getString("paramName"), dataValue); // 写入结果映射
        }
        // 对domain以及path字段处理
        if(dataObj.containsKey("domain")){
            String domainValue = dataObj.getJSONObject("domain").getString("value"); // 读取域名标识
            if(domainValue != null && !domainValue.equals("")){
                // 根据域名标识来获取域名
                Domain domain = domainMapper.getDomainByName(environmentId, domainValue); // 查询域名
                if(domain != null) {
                    dataObj.getJSONObject("domain").put("value", domain.getDomainData()); // 写入域名值
                }
            }else {  // 根据path来获取域名
                if(dataObj.containsKey("path")){
                    String path = dataObj.getJSONObject("path").getString("value"); // 读取path
                    List<Domain> domainList = domainMapper.getPathDomainList(environmentId); // 查询所有域名前缀
                    for(Domain domain: domainList){
                        String domainKey = domain.getDomainKey(); // 域名前缀
                        if(path.startsWith(domainKey)){
                            dataObj.getJSONObject("domain").put("value", domain.getDomainData()); // 匹配后写入域名
                            break;
                        }
                    }
                }
            }
        }
        return dataObj;
    }

    /**
     * 构建API控制器配置
     *
     * @param environmentId // 环境ID，用于数据库连接解析
     * @param controller    // 控制器配置列表（入参/前置/后置）
     * @return JSONObject   // 控制器配置映射（含db连接）
     *
     * 思想：
     *      1. 相关的控制信息均在case_api的controller字段中
     *      2. 通用字段：name,value
     */
    public JSONObject getApiController(String environmentId, JSONArray controller){
        JSONObject controllerObj = new JSONObject(); // 结果映射
        if(controller == null){
            return controllerObj; // 空控制器直接返回
        }
        // 脚本和sql（pre和post）
        JSONArray pre = new JSONArray();
        JSONArray post = new JSONArray();

        // controller:[{name:xx,value:xx},{},{}]
        for(int i =0; i<controller.size(); i++) {
            // 单条控制器项
            JSONObject controllerData = controller.getJSONObject(i);

            // 控制器name&&value
            String controllerName = controllerData.getString("name");
            String controllerValue = controllerData.getString("value"); // 原始值字符串

            // 代理跳过（不在此处处理）
            if(controllerName.equals("proxy")){
                continue;
            }

            // sql（根据数据库名获得数据库相关信息）
            if(controllerName.contains("Sql") && !controllerValue.equals("{}")){ // 处理sql中的数据库连接信息
                JSONObject value = JSONObject.parseObject(controllerValue); // 解析值对象
                Database database = databaseMapper.getDatabaseByName(environmentId, value.getString("db")); // 查询数据库
                JSONObject db = new JSONObject(); // 连接信息占位
                if(database != null){
                    db = JSONObject.parseObject(database.getConnectInfo()); // 连接详情
                    db.put("tpz", database.getDatabaseType()); // 数据库类型
                    db.put("db", database.getDatabaseKey()); // 数据库别名
                }
                value.put("db", db); // 写回连接信息
                controllerData.put("value", value.toJSONString()); // 回写字符串
            }

            if(controllerName.startsWith("pre")){
                pre.add(controllerData); // 收集前置
            }else if(controllerName.startsWith("post")){
                post.add(controllerData); // 收集后置
            }else {
                controllerObj.put(controllerName, controllerData.getString("value")); // 其他直接映射
            }
        }
        if(pre.size()>0){
            controllerObj.put("pre", pre); // 写回前置
        }
        if(post.size()>0){
            controllerObj.put("post", post); // 写回后置
        }
        return controllerObj;
    }

    /**
     * 构建REST接口定义
     *
     * @param rest       // REST定义列表
     * @return JSONObject // path/method/域名签名 等信息
     */
    public JSONObject getApiRest(JSONArray rest){
        JSONObject restObj = new JSONObject(); // 结果映射
        if(rest == null){
            return restObj; // 空REST直接返回
        }
        for(int i =0; i<rest.size(); i++) {
            JSONObject restData = rest.getJSONObject(i); // 单条定义
            restObj.put(restData.getString("name"), restData.getString("value")); // 写入映射
        }
        return restObj;
    }

    /**
     * 构建API查询参数
     *
     * @param query      // 查询参数定义列表
     * @return JSONObject // 查询参数映射
     */
    public JSONObject getApiQuery(JSONArray query){
        JSONObject queryObj = new JSONObject(); // 结果映射
        if(query==null){
            return queryObj; // 空Query直接返回
        }
        for(int i =0; i<query.size(); i++) {
            JSONObject queryData = query.getJSONObject(i); // 单条Query
            queryObj.put(queryData.getString("name"), queryData.getString("value")); // 写入映射
        }
        return queryObj;
    }

    /**
     * 构建API代理配置（排除前后置）
     *
     * @param proxyId    // 代理配置ID
     * @param controller // 控制器列表（用于过滤前置/后置）
     * @return JSONObject // 代理配置映射
     */
    public JSONObject getApiProxy(String proxyId, JSONArray controller){
        if(controller != null) {
            for (int i = 0; i < controller.size(); i++) {   // 优先从接口配置中获取代理
                JSONObject controllerData = controller.getJSONObject(i);
                String controllerName = controllerData.getString("name");
                if (controllerName.equals("proxy")) {
                    return controllerData.getJSONObject("value"); // 命中直接返回
                }
            }
        }
        // 根据公共参数中的proxyId获得proxy
        ParamData paramData = commonParamMapper.getParamById(proxyId);
        try{
            return JSONObject.parseObject(paramData.getParamData());
        }catch (Exception exception) {
            return new JSONObject();
        }
    }

    /**
     * 构建请求头部配置
     *
     * @param headerId   // 头部配置ID
     * @param headerList // 头部列表（KV结构）
     * @return JSONObject // 头部映射
     */
    public JSONObject getApiHeader(String headerId, JSONArray headerList){
        // 合并接口用例请求头
        ParamData paramData = commonParamMapper.getParamById(headerId);
        try{
            JSONObject header = new JSONObject();
            if(paramData != null){
                header = JSONObject.parseObject(paramData.getParamData());
            }
            if(headerList == null){
                return header;
            }
            for(int i =0; i<headerList.size(); i++){
                JSONObject paramObj = headerList.getJSONObject(i);
                String headerKey = paramObj.getString("name");
                String headerValue = paramObj.getString("value");
                for (String item : header.keySet()) {
                    // 用例中的同名header key 替换公参中的 key不区分大小写
                    if (item.equalsIgnoreCase(headerKey)) {
                        header.remove(item);
                        break;
                    }
                }
                header.put(headerKey, headerValue);
            }
            return header;
        }catch (Exception exception) {
            return new JSONObject();
        }
    }

    /**
     * 构建自定义函数列表
     *
     * @param functions // 函数ID列表
     * @return JSONArray // 函数定义列表（name/code/params）
     */
    public JSONArray getCaseFunctions(JSONArray functions){
        /**
         * 思想：遍历函数,然后获得对应的函数(函数有多个，故用[])
         * 最终示例：[ {name:func_name , code:xxx , params:{ "type":[string,int] , "name":[type:string] } ,{}]
         *  [
         *      {
         * 		"code":"xxx",
         * 		"name":"func_name",
         * 		"params":{
         * 			"types":["string","int"],
         * 			"names":["p_name_1","p_name_1"]
         *        }
         *      },
         *      {}
         *  ]
         */

        // 获取用例所需要的自定义函数
        JSONArray functionList = new JSONArray();
        for(int i=0; i<functions.size();i++){
            JSONObject functionObj = new JSONObject();
            String functionId = functions.getString(i);
            Function function = functionMapper.getFunctionDetail(functionId);
            functionObj.put("name", function.getName());
            functionObj.put("code", function.getCode());

            // 封装params
            JSONArray params = JSONArray.parseArray(function.getParam());
            JSONObject paramObj = new JSONObject();
            paramObj.put("names", new JSONArray());
            paramObj.put("types", new JSONArray());
            for(int j=0; j<params.size(); j++){
                JSONObject param = params.getJSONObject(j);
                paramObj.getJSONArray("names").add(param.getString("paramName"));
                paramObj.getJSONArray("types").add(param.getString("type"));
            }
            functionObj.put("params", paramObj);
            functionList.add(functionObj);
        }
        return functionList;
    }

    /**
     * 构建公参列表
     *
     * @param params    // 公参ID列表
     * @return JSONObject // 公参映射（name -> {type,value}）
     */
    public JSONObject getCaseParams(JSONArray params){
        /**
         * 思想：遍历公参id,然后获得对应的数据
         * 最终示例：{"commonParam_1":{type:string,value:xxx},"commonParam2":{}}
         */

        // 获取用例所需要的公参
        JSONObject paramObj = new JSONObject();
        for(int i=0; i<params.size();i++){
            String paramId = params.getString(i);
            ParamData paramData = commonParamMapper.getParamById(paramId);
            JSONObject param = new JSONObject();
            param.put("type", paramData.getDataType());
            param.put("value", paramData.getParamData());
            paramObj.put(paramData.getName(), param);
        }
        return paramObj;
    }

    /**
     * 通过域名签名拼接完整URL
     *
     * @param environmentId // 环境ID
     * @param domainSign    // 域名签名（环境下的域名别名）
     * @param path          // 请求路径
     * @return String       // 完整URL
     *
     */
    public String getUrlBySign( String environmentId, String domainSign, String path){
        // 匹配环境下的域名 匹配不到则为null
        String url = null;
        // 标识非空，则根据id,直接查询
        if(domainSign != null && !domainSign.equals("")){
            Domain domain = domainMapper.getDomainByName(environmentId, domainSign);
            if(domain != null) {
                url = domain.getDomainData();
            }
        }
        // 标识为空，则查询出所有的路由，依次遍历，根据string头匹配，从而更新url
        else {
            List<Domain> domainList = domainMapper.getPathDomainList(environmentId);
            for(Domain domain: domainList){
                String domainKey = domain.getDomainKey();
                if(path.startsWith(domainKey)){
                    url = domain.getDomainData();
                    break;
                }
            }
        }
        return url;
    }

    /**
     * 构建测试集合
     *
     * @param task // 任务信息（来源类型/集合/计划）
     * @return List<TaskTestCollectionResponse> // 测试集合列表
     */
    public List<TaskTestCollectionResponse> getTaskTestCollectionList(TaskDTO task) {
        // 获取每次测试所需的测试任务用例 按照测试集合列表-测试集合(集合下用例列表)-测试用例 维度给出
        // 用例调试以临时数据id为集合id-用例id
        // 用例执行以用例id为 集合id-用例id 都只有一个集合一个用例
        // 集合执行只有一个集合 多条用例 计划执行有多个集合 多条用例

        // 测试集合
        List<TaskTestCollectionResponse> taskTestCollectionList = new ArrayList<>();

        // plan类型task
        if(task.getSourceType().equals(ReportSourceType.PLAN.toString())){
            List<PlanCollectionDTO> planCollections = planCollectionMapper.getPlanCollectionList(task.getSourceId());
            for(PlanCollectionDTO planCollectionDTO:planCollections){
                TaskTestCollectionResponse taskTestCollection = new TaskTestCollectionResponse();
                taskTestCollection.setCollectionId(planCollectionDTO.getCollectionId());
                Collection collection = collectionMapper.getCollectionDetail(planCollectionDTO.getCollectionId());
                if(collection==null) return taskTestCollectionList;
                if(this.getDeviceCouldUsing(collection.getDeviceId(), task.getId())){
                    taskTestCollection.setDeviceId(collection.getDeviceId());
                }else {
                    taskTestCollection.setDeviceId(null);
                }
                taskTestCollection.setDeviceId(collection.getDeviceId());
                List<TaskTestCaseResponse> taskTestCaseList = this.getTaskTestCaseList(planCollectionDTO.getCollectionId());
                taskTestCollection.setTestCaseList(taskTestCaseList);
                taskTestCollectionList.add(taskTestCollection);
            }
        }

        // collection类型task
        else if(task.getSourceType().equals(ReportSourceType.COLLECTION.toString())){
            TaskTestCollectionResponse taskTestCollection = new TaskTestCollectionResponse();
            taskTestCollection.setCollectionId(task.getSourceId());
            Collection collection = collectionMapper.getCollectionDetail(task.getSourceId());
            if(collection==null) return taskTestCollectionList;
            taskTestCollection.setDeviceId(task.getDeviceId());
            List<TaskTestCaseResponse> taskTestCaseList = this.getTaskTestCaseList(task.getSourceId());
            taskTestCollection.setTestCaseList(taskTestCaseList);
            taskTestCollectionList.add(taskTestCollection);
        }

        // case类型task
        else if(task.getSourceType().equals(ReportSourceType.CASE.toString())){
            // 新增test_collection
            TaskTestCollectionResponse taskTestCollection = new TaskTestCollectionResponse();
            taskTestCollection.setCollectionId(task.getSourceId());
            taskTestCollection.setDeviceId(task.getDeviceId());

            // 新增test_case_List
            List<TaskTestCaseResponse> taskTestCaseList = new ArrayList<>();
            TaskTestCaseResponse taskTestCase = new TaskTestCaseResponse();
            taskTestCase.setIndex(1L);                                          // index序号
            taskTestCase.setCaseId(task.getSourceId());                         // 此处source_id=case_id
            // 赋值case_type（根据task的source_id获得case_detail,再根据其case_detail）
            CaseDTO caseDTO = caseMapper.getCaseDetail(task.getSourceId());     // 用例的详细信息（含有List<case_apis>）
            taskTestCase.setCaseType(caseDTO.getType());                        // case_type

            // 赋值
            taskTestCaseList.add(taskTestCase);                     // case_list新增case
            taskTestCollection.setTestCaseList(taskTestCaseList);   // collection更新case_list
            taskTestCollectionList.add(taskTestCollection);         // collection_list新增collection
        }

        // temp类型task
        else if(task.getSourceType().equals(ReportSourceType.TEMP.toString())){
            // 获取临时的Debug数据
            DebugData debugData = debugDataMapper.getDebugData(task.getSourceId());
            CaseRequest caseRequest = JSONObject.parseObject(debugData.getData(), CaseRequest.class);

            // 新增tset_collection
            TaskTestCollectionResponse taskTestCollection = new TaskTestCollectionResponse();
            taskTestCollection.setCollectionId(task.getSourceId());             // collectionId=taskId
            taskTestCollection.setDeviceId(task.getDeviceId());                 // 设备id(App)

            // 新增test_case_List
            List<TaskTestCaseResponse> taskTestCaseList = new ArrayList<>();
            TaskTestCaseResponse taskTestCase = new TaskTestCaseResponse();
            taskTestCase.setIndex(1L);                          // index序号
            taskTestCase.setCaseId(task.getSourceId());         // 此处source_id=DebugData_id
            taskTestCase.setCaseType(caseRequest.getType());    // caseType

            // 赋值
            taskTestCaseList.add(taskTestCase);                 // case_list新增case
            taskTestCollection.setTestCaseList(taskTestCaseList);   // collection更新case_list
            taskTestCollectionList.add(taskTestCollection);         // collection_list新增collection
        }

        return taskTestCollectionList;
    }

    /**
     * 获取集合下的用例列表（函数功能）
     *
     * @param collectionId // 集合标识
     * @return List<TaskTestCaseResponse> // 用例索引列表（含顺序与类型）
     */
    private List<TaskTestCaseResponse> getTaskTestCaseList(String collectionId){
        // 获取任务集合下的用例列表
        List<CollectionCaseDTO> collectionCases = collectionCaseMapper.getCollectionCaseList(collectionId);
        List<TaskTestCaseResponse> taskTestCaseList = new ArrayList<>();
        for(CollectionCaseDTO collectionCaseDTO:collectionCases){
            TaskTestCaseResponse taskTestCase = new TaskTestCaseResponse();
            taskTestCase.setIndex(collectionCaseDTO.getIndex());
            taskTestCase.setCaseId(collectionCaseDTO.getCaseId());
            taskTestCase.setCaseType(collectionCaseDTO.getCaseType());
            taskTestCaseList.add(taskTestCase);
        }
        return taskTestCaseList;
    }

    /**
     * 设备占用与可用性判断（函数功能）
     *
     * @param deviceId // 设备标识
     * @param taskId   // 当前任务标识
     * @return Boolean // 是否可用（并在可用时占用设备）
     */
    private Boolean getDeviceCouldUsing(String deviceId, String taskId){
        if(null == deviceId){
            return false;
        }
        Device device = deviceMapper.getDeviceById(deviceId);
        if(!device.getStatus().equals(DeviceStatus.ONLINE.toString())){
            return false;
        }
        // 占用设备（关键步骤）
        device.setStatus(DeviceStatus.TESTING.toString());
        device.setUpdateTime(System.currentTimeMillis());
        device.setUser(taskId);
        device.setTimeout(-1);  // 测试中设备不予超时
        deviceMapper.updateDevice(device);  // 占用设备
        return true;
    }
}

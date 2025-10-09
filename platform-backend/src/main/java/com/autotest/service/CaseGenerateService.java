package com.autotest.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.autotest.common.utils.StringUtils;
import com.autotest.domain.Api;
import com.autotest.domain.Case;
import com.autotest.domain.CaseApi;
import com.autotest.mapper.ApiMapper;
import com.autotest.mapper.CaseApiMapper;
import com.autotest.mapper.CaseMapper;
import com.autotest.dto.ApiParamRuleDTO;
import com.autotest.dto.ApiParamVerifyDTO;
import com.autotest.request.ApiParamRuleRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.jayway.jsonpath.DocumentContext;
import com.jayway.jsonpath.JsonPath;

import javax.annotation.Resource;
import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;
/**
 * 用例生成服务：自动构造API健壮性测试用例
 * 职责：基于参数规则生成正向/逆向用例，聚合CaseApi并入库。
 * 示例：caseGenerateService.generateCase(req) 入口生成并保存派生步骤
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class CaseGenerateService {

    @Resource
    private ApiMapper apiMapper; // 接口数据访问层

    @Resource
    private CaseMapper caseMapper; // 用例数据访问层

    @Resource
    private CaseApiMapper caseApiMapper; // 用例接口步骤访问层

    private static final Map<String, Object> ParamTypeMap = new HashMap<String, Object>() {{ // 参数类型默认值映射
        put("Int", 100); put("Float", 0.1); put("Boolean", true); // 不同类型参数默认值
        put("String", "test"); put("SpecialStr", "&test@");
    }};

    private static final Map<String, Object[]> ParamRequiredMap = new HashMap<String, Object[]>() {{ // 必填性规则映射
        put("must", new Object[]{"逆向", true, "不能空传", null});    // 用例类型 是否删除该字段 规则描述 字段值
        put("empty", new Object[]{"正向", false, "可以传空", ""});
        put("null", new Object[]{"正向", false, "可以传null", null});
        put("lost", new Object[]{"正向", true, "可以空传", null});
    }};

    /**
     * 入口：根据参数规则批量生成健壮性用例及其接口步骤
     * @param request // 规则请求（包含目标API及各字段规则、断言、创建人信息）
     */
    public void generateCase(ApiParamRuleRequest request) {
        Api api = apiMapper.getApiDetail(request.getApiId());
        // 新增健壮性用例
        Case testCase = new Case();
        testCase.setId(UUID.randomUUID().toString());
        testCase.setName("【健壮性用例】接口 "+api.getName()+" 字段健壮性校验");
        testCase.setType("API");
        testCase.setLevel("P1");
        testCase.setDescription(api.getDescription());
        testCase.setEnvironmentIds("[]");
        testCase.setModuleId("0");
        testCase.setThirdParty("");
        testCase.setProjectId(api.getProjectId());
        testCase.setCommonParam(JSONObject.parseObject(
                "{\"functions\": [], \"params\": [],\"header\": \"\", \"proxy\": \"\"}").toJSONString());
        testCase.setCreateTime(System.currentTimeMillis());
        testCase.setUpdateTime(System.currentTimeMillis());
        testCase.setCreateUser(request.getCreateUser());
        testCase.setUpdateUser(request.getCreateUser());
        testCase.setStatus("Normal");
        caseMapper.addCase(testCase); // 保存用例
        // 生成完整的接口请求作为基线
        List<CaseApi> caseApis = new ArrayList<>();
        CaseApi caseApi = new CaseApi();
        caseApi.setId(UUID.randomUUID().toString());
        caseApi.setCaseId(testCase.getId());
        caseApi.setApiId(api.getId());
        caseApi.setDescription("【正向用例】所有字段正常输入");
        caseApi.setIndex(1L);
        caseApi.setHeader(this.replaceArray(api.getHeader(), request.getHeader())); // 合并请求头
        caseApi.setBody(this.replaceObject(api.getBody(), request.getBody())); // 合并请求体
        caseApi.setQuery(this.replaceArray(api.getQuery(), request.getQuery())); // 合并Query参数
        caseApi.setRest(this.replaceArray(api.getHeader(), request.getHeader())); // 合并REST参数
        caseApi.setRelation("[]");
        caseApi.setAssertion(JSONArray.toJSONString(request.getPositiveAssertion()));
        caseApi.setController(JSONArray.parseArray("[{\"name\": \"errorContinue\", \"value\": true}]").toJSONString());
        caseApis.add(caseApi);
        // 按规则生成派生步骤
        Long index = 1L;    // 接口序号
        // 处理请求头字段规则并派生步骤
        for(ApiParamRuleDTO ruleDTO: request.getHeader()){
            List<ApiParamVerifyDTO> verifyDTOS = this.analysisRule("请求头", ruleDTO);
            for(ApiParamVerifyDTO verifyDTO: verifyDTOS){
                index++;
                caseApis.add(this.getCaseApi(caseApi, index, "header", verifyDTO, request));
            }
        }
        // 处理请求体字段规则并派生步骤
        for(ApiParamRuleDTO ruleDTO: request.getBody()){
            List<ApiParamVerifyDTO> verifyDTOS = this.analysisRule("请求体", ruleDTO);
            for(ApiParamVerifyDTO verifyDTO: verifyDTOS){
                index++;
                caseApis.add(this.getCaseApi(caseApi, index, "body", verifyDTO, request));
            }
        }
        // 处理 Query 字段规则并派生步骤
        for(ApiParamRuleDTO ruleDTO: request.getQuery()){
            List<ApiParamVerifyDTO> verifyDTOS = this.analysisRule("QUERY参数", ruleDTO);
            for(ApiParamVerifyDTO verifyDTO: verifyDTOS){
                index++;
                caseApis.add(this.getCaseApi(caseApi, index, "query", verifyDTO, request));
            }
        }
        // 处理 REST 字段规则并派生步骤
        for(ApiParamRuleDTO ruleDTO: request.getRest()){
            List<ApiParamVerifyDTO> verifyDTOS = this.analysisRule("REST参数", ruleDTO);
            for(ApiParamVerifyDTO verifyDTO: verifyDTOS){
                index++;
                caseApis.add(this.getCaseApi(caseApi, index, "rest", verifyDTO, request));
            }
        }
        caseApiMapper.addCaseApi(caseApis); // 批量保存派生步骤
    }

    /**
     * 基于基线步骤派生单条接口步骤
     * @param temp        // 基线步骤（含完整header/body/query/rest）
     * @param index       // 步骤序号
     * @param replaceType // 替换类型（header/body/query/rest）
     * @param verifyDTO   // 校验描述（方向、类型、值、是否删除等）
     * @param request     // 原始规则请求（用于选择正向/逆向断言集）
     * @return CaseApi    // 派生后的单条步骤
     */
    private CaseApi getCaseApi(CaseApi temp, Long index, String replaceType, ApiParamVerifyDTO verifyDTO, ApiParamRuleRequest request){
        // 构造派生步骤对象并设置基础信息
        CaseApi caseApi = new CaseApi();
        caseApi.setId(UUID.randomUUID().toString());
        caseApi.setCaseId(temp.getCaseId());
        caseApi.setApiId(temp.getApiId());
        caseApi.setDescription(verifyDTO.getDescription());
        caseApi.setIndex(index);
        caseApi.setHeader(replaceType.equals("header")?
                this.replaceArrayWithVerify(temp.getHeader(), verifyDTO):temp.getHeader()); // 定位并替换header
        caseApi.setBody(replaceType.equals("body")?
                this.replaceObjectWithVerify(temp.getBody(), verifyDTO):temp.getBody()); // 定位并替换body
        caseApi.setQuery(replaceType.equals("query")?
                this.replaceArrayWithVerify(temp.getQuery(), verifyDTO):temp.getQuery()); // 定位并替换query
        caseApi.setRest(replaceType.equals("rest")?
                this.replaceArrayWithVerify(temp.getRest(), verifyDTO):temp.getRest()); // 定位并替换rest
        caseApi.setRelation("[]");
        // 根据方向选择断言集
        caseApi.setAssertion(JSONArray.toJSONString(verifyDTO.getDirection().equals("正向") ?
                request.getPositiveAssertion(): request.getOppositeAssertion()));
        caseApi.setController(JSONArray.parseArray("[{\"name\": \"errorContinue\", \"value\": true}]").toJSONString());
        return caseApi;
    }

    /**
     * 在数组型参数中定位并替换/删除指定字段
     * @param data      // 原始数组JSON字符串（header/query/rest/form）
     * @param verifyDTO // 校验规则（字段名、类型、值、是否删除）
     * @return String   // 替换后的JSON字符串
     */
    private String replaceArrayWithVerify(String data, ApiParamVerifyDTO verifyDTO){
        // 替换请求头 查询参数 路径参数 单个参数
        JSONArray params = JSONArray.parseArray(data);
        for(int i=0;i<params.size();i++){
            JSONObject param = params.getJSONObject(i);
            if(verifyDTO.getName().equals(param.getString("name"))){
                if(param.containsKey("type")){
                    param.put("type", verifyDTO.getType());
                }
                if(verifyDTO.getDelete()){
                    params.remove(i); // 删除字段
                }else {
                    param.put("value", verifyDTO.getValue()); // 替换值
                }
                break;
            }
        }
        return params.toJSONString();
    }

    /**
     * 在对象型请求体中按类型定点替换/删除指定字段
     * @param data      // 原始body对象JSON字符串（form/json）
     * @param verifyDTO // 校验规则（字段名、类型、值、是否删除）
     * @return String   // 替换后的JSON字符串
     */
    private String replaceObjectWithVerify(String data, ApiParamVerifyDTO verifyDTO){
        // 替换请求体单个参数
        JSONObject body = JSONObject.parseObject(data);
        String type = body.getString("type");
        if(type.equals("form-data") || type.equals("form-urlencoded")){
            String formData = this.replaceArrayWithVerify(body.getJSONArray("form").toJSONString(), verifyDTO);
            body.put("form", JSONArray.parseArray(formData));
        }else if(type.equals("json")){
            JSONObject json = JSONObject.parseObject(body.getString("json"));
            if(json==null){
                json = new JSONObject();
            }
            if(verifyDTO.getDelete()){
                json = this.deleteJsonWithExpression(json, verifyDTO.getName()); // 删除节点
            }
            json = this.replaceJsonWithExpression(json, verifyDTO.getName(), verifyDTO.getValue()); // 设置值
            body.put("json", json.toJSONString());
        }
        return body.toJSONString();
    }

    /**
     * 批量替换数组型参数的值（按规则名映射）
     * @param data  // 原始数组JSON字符串
     * @param rules // 规则列表（字段名-值）
     * @return String // 替换后的JSON字符串
     */
    private String replaceArray(String data, List<ApiParamRuleDTO> rules){
        // 替换请求头 查询参数 路径参数 所有参数
        JSONArray params = JSONArray.parseArray(data);
        Map<String, ApiParamRuleDTO> ruleMap = rules.stream().collect(
                Collectors.toMap(ApiParamRuleDTO::getName, apiParamRuleDTO -> apiParamRuleDTO));
        for(int i=0;i<params.size();i++){
            JSONObject param = params.getJSONObject(i);
            ApiParamRuleDTO ruleDTO = ruleMap.get(param.getString("name"));
            if(ruleDTO == null){
                continue;   // 字段没做配置则不更改默认值
            }
            param.put("value", ruleDTO.getValue()); // 替换值
        }
        return params.toJSONString();
    }

    /**
     * 批量替换对象型请求体（form/json）的字段值
     * @param data  // 原始对象JSON字符串
     * @param rules // 规则列表（字段名-类型-值）
     * @return String // 替换后的JSON字符串
     */
    private String replaceObject(String data, List<ApiParamRuleDTO> rules){
        // 替换请求体所有参数
        JSONObject body = JSONObject.parseObject(data);
        String type = body.getString("type");
        if(type.equals("form-data") || type.equals("form-urlencoded")){
            String formData = this.replaceArray(body.getJSONArray("form").toJSONString(), rules);
            body.put("form", JSONArray.parseArray(formData)); // 写回表单
        }else if(type.equals("json")){
            JSONObject json = JSONObject.parseObject(body.getString("json"));
            if(json==null){
                json = new JSONObject();
            }
            for (ApiParamRuleDTO apiParamRuleDTO: rules){
                json = this.replaceJsonWithExpression(json, apiParamRuleDTO.getName(),
                        this.convertDataType(apiParamRuleDTO.getType(), apiParamRuleDTO.getValue()));
            }
            body.put("json", json.toJSONString()); // 写回JSON
        }
        return body.toJSONString();
    }

    /**
     * 按 JSONPath 表达式设置节点值
     * @param json       // 原始JSON对象
     * @param expression // JSONPath表达式，如 "$.a.b[0]"
     * @param value      // 待设置的值
     * @return JSONObject // 设置后的JSON对象
     */
    private JSONObject replaceJsonWithExpression(JSONObject json, String expression, Object value){
        DocumentContext ext = JsonPath.parse(json);
        JsonPath p = JsonPath.compile(expression);   // 根据表达式找到该节点
        ext.set(p, value); // 设置值
        return ext.json();
    }

    /**
     * 按 JSONPath 表达式删除节点
     * @param json       // 原始JSON对象
     * @param expression // JSONPath表达式
     * @return JSONObject // 删除后的JSON对象
     */
    private JSONObject deleteJsonWithExpression(JSONObject json, String expression){
        DocumentContext ext = JsonPath.parse(json);
        ext.delete(expression); // 删除节点
        return ext.json();
    }

    /**
     * 将字符串值转换为指定类型
     * @param type  // 目标类型（Int/Float/String/Boolean/SpecialStr等）
     * @param value // 原始值（多数为字符串）
     * @return Object // 转换后的值
     */
    private Object convertDataType(String type, Object value){
        Object result;
        switch (type){
            case "Int":
                result = Integer.parseInt((String) value);
                break;
            case "Float":
                result = Double.parseDouble((String) value);
                break;
            default:
                result = value;
        }
        return result;
    }

    /**
     * 解析单个字段规则，生成对应的验证用例集
     * @param replaceType // 替换范围描述（请求头/请求体/QUERY参数/REST参数）
     * @param rule        // 单字段规则（必填性、类型、范围）
     * @return List<ApiParamVerifyDTO> // 派生的验证描述集合
     */
    private List<ApiParamVerifyDTO> analysisRule(String replaceType, ApiParamRuleDTO rule){
        List<ApiParamVerifyDTO> verifyDTOS = new ArrayList<>();
        // 参数必填性校验
        if(!rule.getRequired().equals("None")) {    // 除选择不校验外
            verifyDTOS.addAll(this.getParamVerifyListWithRequired(replaceType, rule.getName(), rule.getType(), rule.getRequired()));
        }
        // 参数类型校验
        if(!rule.getType().equals("None")) {    // 除选择不校验外
            verifyDTOS.addAll(this.getParamVerifyListWithType(replaceType, rule.getName(), rule.getType()));
        }
        // 参数范围校验
        if(!(rule.getType().equals("Boolean") && rule.getType().equals("None"))){   // 布尔型或者不校验参数类型者不校验范围
            verifyDTOS.addAll(this.getParamVerifyListWithRandom(replaceType, rule.getName(), rule.getType(), rule.getRandom()));
        }
        return verifyDTOS;
    }

    /**
     * 构建必填性校验用例
     * @param replaceType // 替换范围描述
     * @param name        // 字段名
     * @param type        // 字段类型
     * @param required    // 必填性规则（must/empty/null/lost/None）
     * @return List<ApiParamVerifyDTO> // 必填性用例
     */
    private List<ApiParamVerifyDTO> getParamVerifyListWithRequired(String replaceType, String name, String type, String required){
        // 生成字段必填性校验
        List<ApiParamVerifyDTO> verifyDTOS = new ArrayList<>();
        if(required.equals("None")){
            return verifyDTOS;
        }
        Object[] rule = ParamRequiredMap.get(required);
        ApiParamVerifyDTO verifyDTO = new ApiParamVerifyDTO();
        verifyDTO.setName(name);
        verifyDTO.setDirection(rule[0].toString());
        verifyDTO.setType(type.equals("SpecialStr")? "String": type);
        verifyDTO.setDelete((Boolean) rule[1]);
        verifyDTO.setDescription(String.format("【%s用例】校验%s%s类型字段%s必填性校验为:%s",
                rule[0].toString(), replaceType, type, name, rule[2].toString()));
        verifyDTO.setValue(rule[3]);
        verifyDTOS.add(verifyDTO);
        return verifyDTOS;
    }

    /**
     * 构建类型校验用例（尝试使用非期待类型的值）
     * @param replaceType // 替换范围描述
     * @param name        // 字段名
     * @param type        // 期待类型
     * @return List<ApiParamVerifyDTO> // 类型校验用例
     */
    private List<ApiParamVerifyDTO> getParamVerifyListWithType(String replaceType, String name, String type){
        // 生成字段类型校验
        List<ApiParamVerifyDTO> verifyDTOS = new ArrayList<>();
        for(String t: ParamTypeMap.keySet()){
            if (t.equals(type) || (type.equals("SpecialStr") && t.equals("String"))) {
                continue;
            }
            ApiParamVerifyDTO verifyDTO = new ApiParamVerifyDTO();
            verifyDTO.setName(name);
            verifyDTO.setDirection("逆向");
            verifyDTO.setType(t.equals("SpecialStr")? "String": t);
            verifyDTO.setDescription(String.format("【逆向用例】校验%s%s类型字段%s输入%s类型值:%s",
                    replaceType, type, name, t, ParamTypeMap.get(t)));
            verifyDTO.setValue(ParamTypeMap.get(t));
            verifyDTOS.add(verifyDTO);
        }
        return verifyDTOS;
    }

    /**
     * 构建范围/边界值校验用例（最小/最大边界及其之外）
     * @param replaceType // 替换范围描述
     * @param name        // 字段名
     * @param type        // 字段类型（String/SpecialStr/数值等）
     * @param random      // 边界范围表达式，如 "[1,10]"、"(0.1,1.0]"
     * @return List<ApiParamVerifyDTO> // 范围校验用例
     */
    private List<ApiParamVerifyDTO> getParamVerifyListWithRandom(String replaceType, String name, String type, String random){
        // 生成边界值校验
        List<Object[]> randomRules = this.analysisRandom(random);
        List<ApiParamVerifyDTO> verifyDTOS = new ArrayList<>();
        for(Object[] randomRule:randomRules){
            ApiParamVerifyDTO verifyDTO = new ApiParamVerifyDTO();
            verifyDTO.setName(name);
            verifyDTO.setDirection(randomRule[0].toString());
            verifyDTO.setType("String");
            verifyDTO.setDescription(String.format("【%s用例】校验%s%s类型字段%s%s:%s",
                    randomRule[0].toString(), replaceType, type, name, randomRule[1].toString(), randomRule[2].toString()));
            if(type.equals("String")){
                verifyDTO.setValue(StringUtils.randomSimpleString((Integer) randomRule[2]));
            }else if(type.equals("SpecialStr")){
                verifyDTO.setValue(StringUtils.randomSpecialString((Integer) randomRule[2]));
            }else {
                verifyDTO.setType(type);
                verifyDTO.setValue(randomRule[2]);
            }
            verifyDTOS.add(verifyDTO);
        }
        return verifyDTOS;
    }

    /**
     * 解析范围表达式，生成最小/最大边界及其之外的取值
     * @param random // 范围表达式，如 "[1,10]"、"(0.1,1.0]"
     * @return List<Object[]> // 每项：{方向说明, 标签, 值}
     */
    private List<Object[]> analysisRandom(String random){
        List<Object[]> result = new ArrayList<>();
        if(random == null || random.equals("")){
            return result;
        }
        if(!((random.startsWith("[") || random.startsWith("(")) &&
                (random.endsWith("]") || random.endsWith(")")) && random.contains(","))){
            return result;
        }
        String mix = random.substring(1).split(",")[0];
        String max = random.substring(0, random.length()-1).split(",")[1];
        // 判断最大最小可输入值
        Number[] mixList = this.getNumberList(mix, random.startsWith("["), true);
        Number[] maxList = this.getNumberList(max, random.startsWith("]"), false);
        result.add(new Object[]{"正向", "可用最小边界值(长度)", mixList[0]});
        result.add(new Object[]{"逆向", "最小边界值(长度)之外", mixList[1]});
        result.add(new Object[]{"正向", "可用最大边界值(长度)", maxList[0]});
        result.add(new Object[]{"逆向", "最大边界值(长度)之外", maxList[1]});
        return result;
    }

    /**
     * 依据边界表达式的闭合/开区间，计算合法值与非法值
     * @param num       // 边界数值字符串，如 "10" 或 "0.1"
     * @param isContain // 是否包含边界（闭区间）
     * @param isMix     // 是否最小边界（true 最小 / false 最大）
     * @return Number[] // [合法边界值, 非法边界外值]
     */
    public Number[] getNumberList(String num, Boolean isContain, Boolean isMix){
        // 返回列表内容 有效值 无效值
        int decimal = 0;
        if(num.contains(".")){
            decimal = num.split("\\.")[1].length();
        }
        BigDecimal step = BigDecimal.valueOf(1 / Math.pow(10, decimal));
        BigDecimal bdValue = new BigDecimal(num);
        BigDecimal[] result;
        if(isContain){
            if(isMix){
                result = new BigDecimal[]{bdValue, bdValue.subtract(step)};
            }else {
                result = new BigDecimal[]{bdValue, bdValue.add(step)};
            }
        }else {
            if(isMix){
                result = new BigDecimal[]{bdValue.subtract(step), bdValue};
            }else {
                result = new BigDecimal[]{bdValue.add(step), bdValue};
            }
        }
        if(num.contains(".")) {
            return new Number[]{result[0].doubleValue(), result[1].doubleValue()};
        }else {
            return new Number[]{result[0].longValue(), result[1].longValue()};
        }
    }
}

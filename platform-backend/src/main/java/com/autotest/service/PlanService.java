package com.autotest.service;

import com.autotest.common.constants.PlanFrequency;
import com.autotest.common.exception.LMException;
import com.autotest.domain.Plan;
import com.autotest.domain.PlanCollection;
import com.autotest.domain.PlanNotice;
import com.autotest.domain.PlanSchedule;
import com.autotest.mapper.*;
import com.autotest.dto.PlanCollectionDTO;
import com.autotest.dto.PlanDTO;
import com.autotest.request.QueryRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 服务：测试计划维护
 * 职责：计划保存/删除、通知配置、详情获取与列表查询；包含调度时间计算。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class PlanService {

    @Resource
    private PlanMapper planMapper;

    @Resource
    private PlanCollectionMapper planCollectionMapper;

    @Resource
    private PlanScheduleMapper planScheduleMapper;

    @Resource
    private CollectionCaseMapper collectionCaseMapper;

    @Resource
    private PlanNoticeMapper planNoticeMapper;

    /**
     * 保存测试计划（新增或更新）
     *
     * @param planDTO // 计划DTO（含集合与调度）
     * @return void   // 无返回
     */
    public void savePlan(PlanDTO planDTO) {
        if(planDTO.getEnvironmentId() == null || planDTO.getEnvironmentId().equals("")){ // 如果环境未选 则判断每个集合是否都没有API用例和WEB用例
            for(PlanCollectionDTO planCollectionDTO: planDTO.getPlanCollections()){
                List<String> caseTypes = collectionCaseMapper.getCollectionCaseTypes(planCollectionDTO.getCollectionId());
                if(caseTypes.contains(null)){
                    throw new LMException("所选集合中存在API或WEB用例 环境不能为空");
                }
            }
        }

        // 新增 || 更新 计划
        if(planDTO.getId().equals("") || planDTO.getId() == null){ // 新增计划
            planDTO.setId(UUID.randomUUID().toString());
            planDTO.setCreateTime(System.currentTimeMillis());
            planDTO.setUpdateTime(System.currentTimeMillis());
            planDTO.setCreateUser(planDTO.getUpdateUser());
            planMapper.addPlan(planDTO);
            PlanSchedule planSchedule = new PlanSchedule();
            planSchedule.setId(UUID.randomUUID().toString());
            planSchedule.setPlanId(planDTO.getId());
            planSchedule.setStartTime(planDTO.getStartTime());
            planSchedule.setFrequency(planDTO.getFrequency());
            planSchedule.setNextRunTime(convertStrToTime(planDTO.getStartTime()));
            planScheduleMapper.addPlanSchedule(planSchedule);
        }else{ // 修改计划
            planDTO.setUpdateTime(System.currentTimeMillis());
            PlanSchedule planSchedule = planScheduleMapper.getPlanSchedule(planDTO.getId());
            if(!planSchedule.getStartTime().equals(planDTO.getStartTime())){
                // 修改了开始时间 开始时间一定大于当前时间
                planSchedule.setStartTime(planDTO.getStartTime());
                planSchedule.setFrequency(planDTO.getFrequency());
                Long startTime = convertStrToTime(planSchedule.getStartTime());
                planSchedule.setNextRunTime(startTime);
                planScheduleMapper.updatePlanSchedule(planSchedule);
            }else if(!planSchedule.getFrequency().equals(planDTO.getFrequency())){
                // 没有修改开始时间但是修改了执行频率
                planSchedule.setFrequency(planDTO.getFrequency());
                Long startTime = convertStrToTime(planSchedule.getStartTime());
                while (!planDTO.getFrequency().equals(PlanFrequency.ONLY_ONE.toString()) && startTime < System.currentTimeMillis()){ // 找到大于当前时间的日期
                    startTime = getNextRunTime(startTime, planSchedule.getFrequency());
                }
                planSchedule.setNextRunTime(startTime);
                planScheduleMapper.updatePlanSchedule(planSchedule);
            }
            planMapper.updatePlan(planDTO);
        }

        // 整合所有的plan_collection_list
        List<PlanCollection> planCollections = new ArrayList<>();
        for(PlanCollectionDTO planCollectionDTO: planDTO.getPlanCollections()){
            PlanCollection planCollection = new PlanCollection();
            planCollection.setId(UUID.randomUUID().toString());
            planCollection.setPlanId(planDTO.getId());
            planCollection.setCollectionId(planCollectionDTO.getCollectionId());
            planCollections.add(planCollection);
        }
        //先删除全部计划集合
        planCollectionMapper.deletePlanCollection(planDTO.getId());
        if(planCollections.size() > 0) {
            try {
                planCollectionMapper.addPlanCollection(planCollections);
            }catch (Exception e){
                throw new LMException("一个测试计划不能重复选择同一测试集合");
            }
        }
    }

    /**
     * 保存计划通知配置
     *
     * @param planNotice // 通知配置实体
     * @return void      // 无返回
     */
    public void savePlanNotice(PlanNotice planNotice){
        if(planNotice.getId() == null || planNotice.getId().equals("")){
            planNotice.setId(UUID.randomUUID().toString());
            planNoticeMapper.addPlanNotice(planNotice);
        }else {
            planNoticeMapper.updatePlanNotice(planNotice);
        }
    }

    /**
     * 删除计划
     *
     * @param plan  // 计划实体（仅使用id）
     * @return void // 无返回
     */
    public void deletePlan(Plan plan) {
        planMapper.deletePlan(plan.getId());
    }

    /**
     * 查询计划详情
     *
     * @param planId  // 计划ID
     * @return PlanDTO // 计划详情（含集合）
     */
    public PlanDTO getPlanDetail(String planId) {
        PlanDTO planDTO = planMapper.getPlanDetail(planId);
        List<PlanCollectionDTO> planCollectionDTOS = planCollectionMapper.getPlanCollectionList(planId);
        planDTO.setPlanCollections(planCollectionDTOS);

        return planDTO;
    }

    /**
     * 查询计划通知配置
     *
     * @param planId       // 计划ID
     * @return PlanNotice  // 通知配置
     */
    public PlanNotice getPlanNotice(String planId) {
        return planNoticeMapper.getPlanNotice(planId);
    }

    /**
     * 条件查询计划列表
     *
     * @param request           // 查询条件（含项目与关键字）
     * @return List<PlanDTO>    // 计划列表
     */
    public List<PlanDTO> getPlanList(QueryRequest request){
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        return planMapper.getPlanList(request);
    }

    /**
     * 将ISO-8601时间字符串转为毫秒时间戳
     *
     * @param time   // 形如 2023-12-01T12:00:00.000Z
     * @return Long  // 毫秒时间戳
     */
    public static Long convertStrToTime(String time){
        try {
            SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSX");
            Date date = dateFormat.parse(time);
            return date.getTime();
        }catch (Exception e){
            return 0L;
        }
    }

    /**
     * 根据频率计算下次运行时间
     *
     * @param lastTime  // 最近一次时间戳
     * @param frequency // 频率（半小时/一小时/一天/一周/一月）
     * @return Long     // 下次运行时间戳
     */
    public static Long getNextRunTime(Long lastTime, String frequency){
        if(frequency.equals(PlanFrequency.HALF_HOUR.toString())){
            return lastTime + 30*60*1000;
        }else if (frequency.equals(PlanFrequency.ONE_HOUR.toString())){
            return lastTime + 60*60*1000;
        }else if (frequency.equals(PlanFrequency.HALF_DAY.toString())){
            return lastTime + 12*60*60*1000;
        }else if (frequency.equals(PlanFrequency.ONE_DAY.toString())){
            return lastTime + 24*60*60*1000;
        }else if (frequency.equals(PlanFrequency.ONE_WEEK.toString())){
            return lastTime + 7*24*60*60*1000;
        }else if (frequency.equals(PlanFrequency.ONE_MONTH.toString())){
            Calendar c = Calendar.getInstance();
            c.setTime(new Date(lastTime));
            c.add(Calendar.MONTH, 1);
            return c.getTimeInMillis();
        }else {
            return lastTime;
        }
    }
}

package com.autotest.service;

import com.autotest.common.constants.TaskType;
import com.autotest.domain.Notification;
import com.autotest.domain.User;
import com.autotest.dto.ReportDTO;
import com.autotest.dto.TaskDTO;
import com.autotest.mapper.NotificationMapper;
import com.autotest.mapper.ReportMapper;
import com.autotest.mapper.UserMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;
import java.util.UUID;
import cn.hutool.http.HttpUtil;

/**
 * 服务：消息通知
 * 职责：通知的保存/删除/查询，以及基于任务与报告的数据填充与发送。
 * 说明：通过 Webhook 推送到外部平台（如企业微信/钉钉），支持模板变量替换。
 */
@Service
public class NotificationService {

    @Resource
    private NotificationMapper notificationMapper;

    @Resource
    private UserMapper userMapper;

    @Resource
    private ReportMapper reportMapper;

    /**
     * 保存通知配置（新增或更新）
     *
     * @param notification // 通知实体（含名称、类型、Webhook、模板参数等）
     * @return void        // 无返回
     */
    public void saveNotification(Notification notification){
        if(notification.getId() == null || notification.getId().equals("")){
            // 新增通知：补充主键与时间戳
            notification.setId(UUID.randomUUID().toString());
            notification.setCreateTime(System.currentTimeMillis());
            notification.setUpdateTime(System.currentTimeMillis());
        }else{
            // 更新通知
            notification.setUpdateTime(System.currentTimeMillis());
        }
        notificationMapper.saveNotification(notification);
    }

    /**
     * 删除通知配置
     *
     * @param id   // 通知ID
     * @return void // 无返回
     */
    public void deleteNotification(String id){
        notificationMapper.deleteNotification(id);
    }

    /**
     * 查询通知详情
     *
     * @param id            // 通知ID
     * @return Notification // 通知详情
     */
    public Notification getNotificationById(String id){
        return notificationMapper.getNotificationById(id);
    }

    /**
     * 条件查询通知列表
     *
     * @param projectId              // 项目ID
     * @param condition              // 关键字（支持模糊）
     * @return List<Notification>    // 通知列表
     */
    public List<Notification> getNotificationList(String projectId, String condition) {
        if(condition != null && !condition.equals("")){
            condition = "%"+condition+"%";
        }
        return notificationMapper.getNotificationList(projectId, condition);
    }

    /**
     * 发送通知消息
     *
     * @param notification // 通知配置（包含模板与Webhook）
     * @param task         // 任务信息（含类型、报告ID、创建人等）
     * @return void        // 无返回
     */
    public void sendNotification(Notification notification, TaskDTO task){
        String taskType = null;
        if(task.getType().equals(TaskType.RUN.toString())){
            taskType = "手工执行";
        }else {
            taskType = "定时任务";
        }
        // 查询报告与用户信息，准备模板变量
        ReportDTO report = reportMapper.getReportDetail(task.getReportId());
        User user = userMapper.getUserInfo(task.getCreateUser());
        Long during = (report.getEndTime() - report.getStartTime()) / 1000;
        // 模板变量替换，生成最终推送内容
        String params = notification.getParams().
                replace("{reportTitle}", report.getName()).
                replace("{taskType}", taskType).
                replace("{user}", user.getAccount()).
                replace("{caseNum}", report.getTotal().toString()).
                replace("{caseSuccess}", report.getPassCount().toString()).
                replace("{caseFail}", report.getFailCount().toString()).
                replace("{caseError}", report.getErrorCount().toString()).
                replace("{successPercent}", report.getPassRate()).
                replace("{executeTime}", during +"S");
        // 通过 Webhook 推送到外部平台
        HttpUtil.post(notification.getWebhookUrl(), params);
    }

}

package com.autotest.mapper;

import com.autotest.domain.Notification;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：通知渠道配置
 * 职责：保存/删除通知、按ID查询与条件列表查询。
 */
@Mapper
public interface NotificationMapper {

    /**
     * 保存通知配置（新增或更新）
     * @param notification 通知实体
     */
    void saveNotification(Notification notification);

    /**
     * 删除通知配置
     * @param id 通知ID
     */
    void deleteNotification(String id);

    /**
     * 按ID查询通知配置
     * @param id        通知ID
     * @return Notification 通知实体
     */
    Notification getNotificationById(String id);

    /**
     * 条件查询通知列表
     * @param projectId 项目ID
     * @param condition 关键字（支持模糊）
     * @return List<Notification> 通知列表
     */
    List<Notification> getNotificationList(String projectId, String condition);

}

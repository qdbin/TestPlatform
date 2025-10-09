package com.autotest.dto;

import com.autotest.domain.Notification;
import lombok.Data;

/**
 * DTO：通知扩展视图（继承 Notification）
 * 用途：用于接口返回与视图层展示，当前与基础实体一致，保留扩展点。
 */
@Data
public class NotificationDTO extends Notification {
    
}

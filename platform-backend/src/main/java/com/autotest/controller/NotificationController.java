package com.autotest.controller;

import com.autotest.common.utils.PageUtils;
import com.autotest.common.utils.Pager;
import com.autotest.domain.Notification;
import com.autotest.request.QueryRequest;
import com.autotest.service.NotificationService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 控制器：通知配置入口
 * 职责：保存、删除、项目通知查询与分页列表
 */
@RestController
@RequestMapping("/autotest/notification")
public class NotificationController {

    @Resource
    private NotificationService notificationService;

    /**
     * 功能：保存通知配置
     *
     * @param notificationRequest // 通知实体
     * @return void               // 无返回
     */
    @PostMapping("/save")
    public void saveNotification(@RequestBody Notification notificationRequest){
        notificationService.saveNotification(notificationRequest);
    }

    /**
     * 功能：删除通知配置
     *
     * @param notification // 通知实体（仅使用id）
     * @return void        // 无返回
     */
    @PostMapping("/delete")
    public void deleteNotification(@RequestBody Notification notification){
        notificationService.deleteNotification(notification.getId());
    }

    /**
     * 功能：查询项目下所有通知配置
     *
     * @param projectId // 项目ID
     * @return List<Notification> // 通知列表
     */
    @GetMapping("/list/{projectId}")
    public List<Notification> getNotificationList(@PathVariable String projectId) {
        return notificationService.getNotificationList(projectId, null);
    }

    /**
     * 功能：分页查询通知列表
     *
     * @param goPage    // 页码
     * @param pageSize  // 每页大小
     * @param request   // 查询请求
     * @return Pager<List<Notification>> // 分页封装的通知列表
     */
    @PostMapping("/list/{goPage}/{pageSize}")
    public Pager<List<Notification>> getNotificationPageList(@PathVariable int goPage, @PathVariable int pageSize,
                                                   @RequestBody QueryRequest request) {
        Page<Object> page = PageHelper.startPage(goPage, pageSize, true);
        return PageUtils.setPageInfo(page, notificationService.getNotificationList(request.getProjectId(), request.getCondition()));
    }

}

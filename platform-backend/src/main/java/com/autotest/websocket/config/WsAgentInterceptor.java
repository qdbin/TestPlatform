package com.autotest.websocket.config;

import com.autotest.domain.Project;
import com.autotest.domain.User;
import com.autotest.mapper.ProjectMapper;
import com.autotest.mapper.UserMapper;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.http.server.ServletServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;

import javax.annotation.Resource;
import java.util.Map;

/**
 * 拦截器：Agent握手参数校验与归一
 * 作用：在WebSocket握手前校验并归一化 owner 与 project，写入会话属性
 * 说明：支持将用户名/项目名转换为系统内的用户ID/项目ID；system 为保留值直传
 */
@Component
public class WsAgentInterceptor implements HandshakeInterceptor {

    @Resource
    private UserMapper userMapper;

    @Resource
    private ProjectMapper projectMapper;

    /**
     * 功能：握手前参数校验与归一
     *
     * @param request     // HTTP请求（读取owner/project）
     * @param response    // HTTP响应
     * @param wsHandler   // WebSocket处理器
     * @param attributes  // 会话属性存储
     * @return boolean    // 校验通过返回true
     *
     * 示例：
     *     owner="张三" -> 转换为用户id；project="Demo" -> 转换为项目id
     */
    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response, WebSocketHandler wsHandler, Map<String, Object> attributes) throws Exception {
        ServletServerHttpRequest req = (ServletServerHttpRequest) request;
        String owner = req.getServletRequest().getParameter("owner");      // 原始用户名或system
        String project = req.getServletRequest().getParameter("project");  // 原始项目名或system
        if(owner != null && !owner.equals("system")) {
            User user = userMapper.getUser(owner);
            if (user == null) {
                return false;
            } else {
                owner = user.getId(); // 转换为用户id
            }
        }else {
            owner = "system";
        }
        if(project != null && !project.equals("system")) {
            Project project1 = projectMapper.getProjectByName(project);
            if (project1 == null) {
                return false;
            } else {
                project = project1.getId(); // 转换为项目id
            }
        }else {
            project = "system";
        }
        attributes.put("owner", owner);     // 设置会话属性
        attributes.put("project", project); // 设置会话属性
        return true;
    }

    /**
     * 功能：握手后处理（当前无需处理）
     */
    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response, WebSocketHandler wsHandler, Exception exception) {

    }

}
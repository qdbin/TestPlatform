package com.autotest.websocket.config;

import com.autotest.websocket.DeviceHeartBeatHandler;
import com.autotest.websocket.EngineHeartBeatHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

/**
 * 配置：WebSocket心跳路由
 * 用途：注册设备/引擎心跳端点与拦截器
 */
@EnableWebSocket
@Configuration
public class WebSocketConfig implements WebSocketConfigurer {

    @Autowired
    private DeviceHeartBeatHandler deviceHeartBeatHandler; // 设备心跳处理器

    @Autowired
    private EngineHeartBeatHandler engineHeartBeatHandler; // 引擎心跳处理器

    @Autowired
    private WsAgentInterceptor wsAgentInterceptor; // 设备端拦截器（会话鉴权/标识）

    @Autowired
    private WsEngineInterceptor wsEngineInterceptor; // 引擎端拦截器（会话鉴权/标识）


    /**
     * 注册WebSocket处理器与拦截器
     *
     * @param registry // 处理器注册器
     * @return void    // 无返回
     *
     * 说明：设置允许跨域以支持控制台页面调试
     */
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(deviceHeartBeatHandler, "/websocket/agent/heartbeat")
                .addInterceptors(wsAgentInterceptor)
                .setAllowedOrigins("*"); // 解决跨域问题
        registry.addHandler(engineHeartBeatHandler, "/websocket/engine/heartbeat")
                .addInterceptors(wsEngineInterceptor)
                .setAllowedOrigins("*"); // 解决跨域问题
    }
}

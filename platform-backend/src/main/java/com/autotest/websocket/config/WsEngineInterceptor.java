package com.autotest.websocket.config;

import com.autotest.common.exception.EngineVerifyException;
import com.autotest.mapper.EngineMapper;
import com.autotest.dto.EngineDTO;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.http.server.ServletServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;

import javax.annotation.Resource;
import java.util.Map;

/**
 * 拦截器：Engine握手鉴权
 * 作用：在WebSocket握手前校验 engineCode 和 engineSecret，通过后写入会话属性
 * 说明：校验失败抛出 EngineVerifyException，阻止握手继续
 */
@Component
public class WsEngineInterceptor implements HandshakeInterceptor {

    @Resource
    private EngineMapper engineMapper;

    /**
     * 功能：引擎握手前鉴权
     *
     * @param request     // HTTP请求（读取engineCode/engineSecret）
     * @param response    // HTTP响应
     * @param wsHandler   // WebSocket处理器
     * @param attributes  // 会话属性存储
     * @return boolean    // 校验通过返回true
     *
     * 示例：engineCode="E001"，engineSecret="xxx" -> 校验通过并写入attributes
     */
    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response, WebSocketHandler wsHandler, Map<String, Object> attributes) throws Exception {
        // 转换为http请求，从查询参数中获取enginCode和enginSecret
        ServletServerHttpRequest req = (ServletServerHttpRequest) request;
        String engineCode = req.getServletRequest().getParameter("engineCode");     // 引擎编码
        String engineSecret = req.getServletRequest().getParameter("engineSecret"); // 引擎密钥
        EngineDTO engineDTO =  engineMapper.getEngineById(engineCode);
        if(!engineSecret.equals(engineDTO.getSecret())){
            throw new EngineVerifyException("code或secret填写不正确");
        }
        attributes.put("engineCode", engineCode);       // 设置会话属性
        attributes.put("engineSecret", engineSecret);   // 设置会话属性
        return true;
    }

    /**
     * 功能：握手后处理（当前无需处理）
     */
    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response, WebSocketHandler wsHandler, Exception exception) {

    }

}
package com.autotest.websocket;

import com.autotest.common.constants.EngineStatus;
import com.autotest.domain.Engine;
import com.autotest.mapper.EngineMapper;
import com.autotest.websocket.config.WsSessionManager;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import javax.annotation.Resource;

/**
 * 处理器：引擎心跳会话
 * 用途：维护引擎在线状态与心跳更新时间
 */
@Component
public class EngineHeartBeatHandler extends TextWebSocketHandler {

    @Resource
    private EngineMapper engineMapper;

    /**
     * socket 建立连接时
     */
    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        // 通过enginCode获得引擎信息
        String engineCode = (String) session.getAttributes().get("engineCode");
        Engine engine = engineMapper.getEngineById(engineCode);

        // 若引擎为离线，则更新为在线
        if (engine.getStatus().equals(EngineStatus.OFFLINE.toString())){
            engineMapper.updateStatus(engineCode, EngineStatus.ONLINE.toString());
        }
        engineMapper.updateHeartbeat(engineCode, System.currentTimeMillis());

        // 将引擎添加到会话池
        WsSessionManager.add("engine", engineCode, session);
    }

    /**
     * 接收消息事件
     */
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        // 更新心跳，更新数据库最后一次的心跳时间
        String engineCode = (String) session.getAttributes().get("engineCode");
        engineMapper.updateHeartbeat(engineCode, System.currentTimeMillis());
    }

    /**
     * socket 断开连接时
     */
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        // 根据enginCode修改为离线状态
        String engineCode = (String) session.getAttributes().get("engineCode");
        if(engineCode == null){
            return;
        }
        Engine engine = engineMapper.getEngineById(engineCode);
        if (!engine.getStatus().equals(EngineStatus.OFFLINE.toString())){
            engineMapper.updateStatus(engineCode, EngineStatus.OFFLINE.toString());
        }

        // 移除会话池
        WsSessionManager.remove("engine", engineCode);
    }
}
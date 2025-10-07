package com.autotest.websocket.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.web.socket.WebSocketSession;
import java.util.concurrent.ConcurrentHashMap;



/**
 * 工具：WebSocket会话管理（agent:engine）
 * 用途：维护设备与引擎端的会话池，支持添加/删除/获取
 */
@Slf4j
public class WsSessionManager {
    /**
     * 保存连接 session 的地方
     */
    private static ConcurrentHashMap<String, WebSocketSession> AGENT_SESSION_POOL = new ConcurrentHashMap<>(); // 设备端会话池

    private static ConcurrentHashMap<String, WebSocketSession> ENGINE_SESSION_POOL = new ConcurrentHashMap<>(); // 引擎端会话池

    /**
     * 添加会话
     *
     * @param type    // 类型（agent/engine）
     * @param key     // 会话键
     * @param session // 会话对象
     */
    public static void add(String type, String key, WebSocketSession session) {
        if(type.equals("agent")) {
            AGENT_SESSION_POOL.put(key, session);   // 加入设备会话池
        }else {
            ENGINE_SESSION_POOL.put(key, session);  // 加入引擎会话池
        }
    }

    /**
     * 删除会话
     *
     * @param type // 类型（agent/engine）
     * @param key  // 会话键
     */
    public static void remove(String type, String key) {
        if(type.equals("agent")) {
            AGENT_SESSION_POOL.remove(key);   // 移除设备会话
        }else {
            ENGINE_SESSION_POOL.remove(key);  // 移除引擎会话
        }
    }

    /**
     * 获取会话
     *
     * @param type // 类型（agent/engine）
     * @param key  // 会话键
     * @return WebSocketSession // 对应会话
     */
    public static WebSocketSession get(String type, String key) {
        if(type.equals("agent")) {
            return AGENT_SESSION_POOL.get(key);   // 获取设备会话
        }else {
            return ENGINE_SESSION_POOL.get(key);  // 获取引擎会话
        }
    }
}
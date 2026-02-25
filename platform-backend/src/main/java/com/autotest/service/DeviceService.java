package com.autotest.service;

import com.alibaba.fastjson.JSONObject;
import com.autotest.common.constants.DeviceStatus;
import com.autotest.domain.Device;
import com.autotest.mapper.DeviceMapper;
import com.autotest.dto.DeviceDTO;
import com.autotest.request.QueryRequest;
import com.autotest.websocket.config.WsSessionManager;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import javax.annotation.Resource;
import java.util.HashMap;
import java.util.List;

/**
 * 服务：设备管理
 * 职责：设备的详情、占用/释放、激活、更新，系统/条件筛选与列表查询。
 * 说明：包含占用状态流转与通过 WebSocket 通知客户端的冷却指令下发。
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class DeviceService {

    @Resource
    private DeviceMapper deviceMapper;

    /**
     * 查询设备详情
     *
     * @param deviceId // 设备ID
     * @return Device  // 设备详情
     */
    public Device getDeviceDetail(String deviceId){
        return deviceMapper.getDeviceById(deviceId);
    }

    /**
     * 停止使用设备（释放占用）
     *
     * @param deviceId // 设备ID
     * @return void    // 无返回
     */
    public void stopUseDevice(String deviceId){
        Device device = deviceMapper.getDeviceById(deviceId);
        this.coldDevice(device);
    }

    /**
     * 冷却设备：重置状态并通知客户端
     *
     * @param device // 设备实体
     * @return void  // 无返回
     */
    public void coldDevice(Device device) {
        device.setStatus(DeviceStatus.COLDING.toString());
        device.setUpdateTime(System.currentTimeMillis());
        device.setSources("{}");
        device.setUser("");
        device.setTimeout(0);
        deviceMapper.updateDevice(device);
        // 通过 WebSocket 通知客户端执行冷却指令
        try {
            WebSocketSession session = WsSessionManager.get("agent", device.getAgent());
            session.sendMessage(new TextMessage("cold@"+device.getSerial()));
        }catch (Exception ignored){
            // 忽略通知异常，保证主流程不受影响
        }
    }

    /**
     * 激活设备：同使用人且状态为使用中，则刷新更新时间
     *
     * @param deviceId // 设备ID
     * @param user     // 当前用户
     * @return Boolean // 是否激活成功
     */
    public Boolean activeDevice(String deviceId, String user) {
        Device device = deviceMapper.getDeviceById(deviceId);
        if(user.equals(device.getUser()) && device.getStatus().equals(DeviceStatus.USING.toString())){
            device.setUpdateTime(System.currentTimeMillis());
            deviceMapper.updateDevice(device);
            return true;
        }
        return false;
    }

    /**
     * 更新设备信息
     *
     * @param device // 设备实体
     * @return void  // 无返回
     */
    public void updateDevice(Device device) {
        device.setUpdateTime(System.currentTimeMillis());
        deviceMapper.updateDevice(device);
    }

    /**
     * 占用设备（设置占用超时时间）
     *
     * @param deviceId // 设备ID
     * @param timeout  // 超时时间（分钟）
     * @param user     // 占用用户
     * @return Boolean // 是否占用成功
     */
    public Boolean useDevice(String deviceId, Integer timeout, String user) {
        Device device = deviceMapper.getDeviceById(deviceId);
        if(!device.getStatus().equals(DeviceStatus.ONLINE.toString())){
            return false;   // 设备非空闲状态无法使用
        }
        device.setStatus(DeviceStatus.USING.toString());
        device.setUpdateTime(System.currentTimeMillis());
        device.setUser(user);
        device.setTimeout(timeout);
        deviceMapper.updateDevice(device);
        return true;
    }

    /**
     * 条件查询设备列表（含过滤器解析）
     *
     * @param request // 查询请求（项目/关键字/状态/过滤器）
     * @param owner   // 设备归属用户
     * @return List<DeviceDTO> // 设备列表
     */
    public List<DeviceDTO> getDeviceList(QueryRequest request, String owner) {
        if(request.getCondition() != null && !request.getCondition().equals("")){
            request.setCondition("%"+request.getCondition()+"%");
        }
        JSONObject filter = request.getFilter();
        List<String> brand = null;
        List<String> android = null;
        List<String> apple = null;
        List<String> size = null;
        if(filter != null) {
            brand = filter.getJSONArray("brand").toJavaList(String.class);
            android = filter.getJSONArray("android").toJavaList(String.class);
            apple = filter.getJSONArray("apple").toJavaList(String.class);
            size = filter.getJSONArray("size").toJavaList(String.class);
        }
        return deviceMapper.getDeviceList(request.getProjectId(), owner, request.getCondition(), request.getStatus(), brand, android, apple, size);
    }

    /**
     * 按系统类型查询设备列表
     *
     * @param projectId // 项目ID
     * @param system    // 系统类型（android/apple/web等）
     * @param owner     // 设备归属用户
     * @return List<Device> // 设备列表
     */
    public List<Device> getDeviceListBySystem(String projectId, String system, String owner){
        return deviceMapper.getDeviceListBySystem(projectId, owner, system);
    }

    /**
     * 获取设备筛选条件
     *
     * @param owner     // 设备归属用户
     * @param projectId // 项目ID
     * @return HashMap<String, List<String>> // 品牌、版本、尺寸等筛选项
     */
    public HashMap<String, List<String>> getDeviceFilter(String owner, String projectId){
        HashMap<String, List<String>> filter = new HashMap<>();
        filter.put("brand", deviceMapper.getDeviceFilter(projectId, owner, "brand", null));
        filter.put("android", deviceMapper.getDeviceFilter(projectId, owner, "version", "android"));
        filter.put("apple", deviceMapper.getDeviceFilter(projectId, owner, "version", "apple"));
        filter.put("size", deviceMapper.getDeviceFilter(projectId, owner, "size", null));
        return filter;
    }

}

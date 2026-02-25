package com.autotest.controller;

import com.autotest.domain.Device;
import com.autotest.dto.DeviceDTO;
import com.autotest.request.QueryRequest;
import com.autotest.service.DeviceService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;

/**
 * 控制器：设备管理
 * 职责：设备筛选、占用/释放、激活、更新，以及明细与列表查询。
 */
@RestController
@RequestMapping("/autotest/device")
public class DeviceController {

    @Resource
    private DeviceService deviceService;

    /**
     * 获取设备筛选条件
     *
     * @param projectId // 项目ID
     * @param request   // 请求上下文（用于获取userId）
     * @return HashMap<String, List<String>> // 设备筛选项集合
     */
    @GetMapping("/filter/{projectId}")
    public HashMap<String, List<String>> getDeviceFilter(@PathVariable String projectId, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        return deviceService.getDeviceFilter(user, projectId);
    }

    /**
     * 停止使用设备（释放占用）
     *
     * @param deviceId // 设备ID
     * @return void    // 无返回
     */
    @PostMapping("/stop/{deviceId}")
    public void stopUseDevice(@PathVariable String deviceId) {
        deviceService.stopUseDevice(deviceId);
    }

    /**
     * 激活设备
     *
     * @param deviceId // 设备ID
     * @param request  // 请求上下文（用于获取userId）
     * @return Boolean // 是否激活成功
     */
    @PostMapping("/active/{deviceId}")
    public Boolean activeDevice(@PathVariable String deviceId, HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        return deviceService.activeDevice(deviceId, user);
    }

    /**
     * 更新设备信息
     *
     * @param device // 设备实体
     * @return void  // 无返回
     */
    @PostMapping("/update")
    public void updateDevice(@RequestBody Device device) {
        deviceService.updateDevice(device);
    }

    /**
     * 占用设备（设置占用超时时间）
     *
     * @param deviceId // 设备ID
     * @param timeout  // 占用超时时间（分钟）
     * @param request  // 请求上下文（用于获取userId）
     * @return Boolean // 是否占用成功
     */
    @PostMapping("/use/{deviceId}/{timeout}")
    public Boolean UseDevice(@PathVariable String deviceId, @PathVariable Integer timeout,  HttpServletRequest request) {
        String user = request.getSession().getAttribute("userId").toString();
        return deviceService.useDevice(deviceId, timeout, user);
    }

    /**
     * 查询设备详情
     *
     * @param deviceId // 设备ID
     * @return Device  // 设备详情
     */
    @GetMapping("/detail/{deviceId}")
    public Device getDeviceDetail(@PathVariable String deviceId) {
        return deviceService.getDeviceDetail(deviceId);
    }

    /**
     * 条件查询设备列表
     *
     * @param queryRequest // 查询条件（项目/关键字等）
     * @param request      // 请求上下文（用于获取userId）
     * @return List<DeviceDTO> // 设备列表
     */
    @PostMapping("/list")
    public List<DeviceDTO> getDeviceList(@RequestBody QueryRequest queryRequest, HttpServletRequest request){
        String user = request.getSession().getAttribute("userId").toString();
        return deviceService.getDeviceList(queryRequest, user);
    }

    /**
     * 按系统类型查询设备列表
     *
     * @param system    // 系统类型（android/apple/web等）
     * @param projectId // 项目ID
     * @param request   // 请求上下文（用于获取userId）
     * @return List<Device> // 设备列表
     */
    @GetMapping("/{system}/list/{projectId}")
    public List<Device> getDeviceListBySystem(@PathVariable String system, @PathVariable String projectId, HttpServletRequest request){
        String user = request.getSession().getAttribute("userId").toString();
        return deviceService.getDeviceListBySystem(projectId, system, user);
    }

}

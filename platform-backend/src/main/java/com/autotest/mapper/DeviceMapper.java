package com.autotest.mapper;

import com.autotest.domain.Device;
import com.autotest.dto.DeviceDTO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射：设备数据访问（add:update:query）
 * 用途：设备增改、按条件/系统查询与超时筛查
 */
@Mapper
public interface DeviceMapper {
    /**
     * 新增设备
     *
     * @param device // 设备实体
     * @return void  // 无返回
     */
    void addDevice(Device device);

    /**
     * 更新设备信息
     *
     * @param device // 设备实体
     * @return void  // 无返回
     */
    void updateDevice(Device device);

    /**
     * 通过代理ID更新设备（心跳关联）
     *
     * @param agent // 代理ID
     * @return void // 无返回
     */
    void updateDeviceByAgent(String agent);

    /**
     * 查询超时设备（占用超时/心跳超时）
     *
     * @return List<Device> // 超时设备列表
     */
    List<Device> selectTimeoutDevice();

    /**
     * 条件查询设备列表（含过滤器）
     *
     * @param projectId // 项目ID
     * @param owner     // 设备归属用户
     * @param condition // 关键字（支持模糊）
     * @param status    // 状态筛选（online/offline/using）
     * @param brand     // 品牌过滤
     * @param android   // Android版本过滤
     * @param apple     // iOS版本过滤
     * @param size      // 尺寸过滤
     * @return List<DeviceDTO> // 设备DTO列表
     *
     *     示例：condition="%pixel%"，brand=["Google"], android=["13"], size=["6.3"]
     */
    List<DeviceDTO> getDeviceList(String projectId, String owner, String condition, String status, List<String> brand,
                                  List<String> android, List<String> apple, List<String> size);

    /**
     * 按系统类型查询设备列表
     *
     * @param projectId // 项目ID
     * @param owner     // 设备归属用户
     * @param system    // 系统类型（android/apple/web等）
     * @return List<Device> // 设备列表
     */
    List<Device> getDeviceListBySystem(String projectId, String owner, String system);

    /**
     * 获取设备筛选项（品牌/版本/尺寸）
     *
     * @param projectId // 项目ID
     * @param owner     // 设备归属用户
     * @param field     // 筛选字段（brand/version/size）
     * @param system    // 系统类型（version按系统细分）
     * @return List<String> // 筛选值列表
     */
    List<String> getDeviceFilter(String projectId, String owner, String field, String system);

    /**
     * 根据序列号查询设备
     *
     * @param serial // 设备序列号
     * @return Device // 设备实体
     */
    Device getDeviceBySerial(String serial);

    /**
     * 根据ID查询设备
     *
     * @param id // 设备ID
     * @return Device // 设备实体
     */
    Device getDeviceById(String id);
}
package com.autotest.dto;

import com.autotest.domain.Device;
import lombok.Getter;
import lombok.Setter;

/**
 * 实体：设备传输对象（继承:Device）
 * 扩展：username（展示维护人名称）
 */
@Getter
@Setter
public class DeviceDTO extends Device {

    private String username; // 创建/维护人名称
}

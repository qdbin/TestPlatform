package com.autotest.mapper;

import com.autotest.domain.Driver;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 映射器：驱动管理
 * 职责：按名称/ID查询、保存、删除与列表查询驱动。
 */
@Mapper
public interface DriverMapper {

    /**
     * 根据名称查询驱动
     *
     * @param projectId    // 项目ID
     * @param name         // 驱动名称
     * @return Driver      // 驱动实体（不存在返回null）
     *
     * 示例(Example):
     *     // 入参示例
     *     projectId = "P001"; name = "ChromeDriver";
     *     // 调用示例
     *     driver = mapper.getDriverByName(projectId, name);
     *     // 返回示例（处理后）
     *     driver = {id:"...", name:"ChromeDriver", setting:"{...}"}
     */
    Driver getDriverByName(String projectId, String name);

    /**
     * 根据ID查询驱动
     *
     * @param id         // 驱动ID
     * @return Driver    // 驱动实体（不存在返回null）
     *
     * 示例(Example): id="D001" -> 返回对应驱动详情
     */
    Driver getDriverById(String id);

    /**
     * 保存驱动（新增或更新）
     *
     * @param driver      // 驱动实体（新增需生成ID；更新需传入ID）
     * @return void       // 无返回
     *
     * 示例(Example):
     *     // 新增：driver = {name:"ChromeDriver", setting:"{...}", projectId:"P001"}
     *     // 更新：driver = {id:"D001", name:"ChromeDriver", setting:"{...}"}
     */
    void saveDriver(Driver driver);

    /**
     * 删除驱动
     *
     * @param id     // 驱动ID
     * @return void  // 无返回
     *
     * 示例(Example): id="D001" -> 删除该驱动
     */
    void deleteDriver(String id);

    /**
     * 条件查询驱动列表
     *
     * @param projectId      // 项目ID
     * @param condition      // 关键字（支持模糊；外部需预处理如 "%kw%"）
     * @return List<Driver>  // 驱动列表
     *
     * 示例(Example):
     *     // 入参：projectId="P001", condition="%Chrome%"
     *     // 返回：[{name:"ChromeDriver"}, {name:"ChromiumDriver"}]
     */
    List<Driver> getDriverList(String projectId, String condition);
}

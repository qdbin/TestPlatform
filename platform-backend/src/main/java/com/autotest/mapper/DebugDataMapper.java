package com.autotest.mapper;

import com.autotest.domain.DebugData;
import org.apache.ibatis.annotations.Mapper;


/**
 * 映射：接口调试数据
 * 用途：新增调试数据、按ID查询与删除
 */
@Mapper
public interface DebugDataMapper {
    /**
     * 新增调试数据
     *
     * @param debugData // 调试数据实体
     * @return void     // 无返回
     */
    void addDebugData(DebugData debugData);

    /**
     * 查询调试数据详情
     *
     * @param id        // 调试数据ID
     * @return DebugData // 调试数据实体
     */
    DebugData getDebugData(String id);

    /**
     * 删除调试数据
     *
     * @param id    // 调试数据ID
     * @return void // 无返回
     */
    void deleteDebugData(String id);
}
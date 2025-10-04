package com.autotest.common.utils;

import com.github.pagehelper.Page;

/**
 * 工具：分页结果组装（page:list）
 * 用途：将 Page 信息与数据列表封装为统一 Pager
 */
public class PageUtils {
    /**
     * 设置分页对象信息并返回
     * @param page    // PageHelper分页对象（提供总条数）
     * @param obj     // 数据列表对象（任意类型）
     * @return Pager  // 统一分页响应对象
     * 示例：
     *     page.getTotal()=120，obj=List<DTO>
     *     调用：PageUtils.setPageInfo(page, obj)
     *     返回：Pager{list=obj, total=120}
     */
    public static <T> Pager<T> setPageInfo(Page<Object> page, T obj) {
        try {
            Pager<T> pager = new Pager<>();
            pager.setList(obj);              // 设置数据列表
            pager.setTotal(page.getTotal()); // 设置总条数
            return pager;                    // 返回统一分页对象
        } catch (Exception e) {
            throw new RuntimeException("Error saving current page number data！");
        }
    }
}

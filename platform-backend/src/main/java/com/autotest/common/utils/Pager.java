package com.autotest.common.utils;

/**
 * 实体：分页响应载体（list:total）
 * 说明：封装数据列表与总条数字段，用于统一分页结果
 */
public class Pager<T> {
    private T list;    // 数据列表
    private long total; // 总条数

    public Pager() {
    }

    public Pager(T list, long total, long pageCount) {
        this.list = list;   // 赋值数据列表
        this.total = total; // 赋值总条数
    }

    public long getTotal() {
        return total;       // 返回总条数
    }

    public void setTotal(long total) {
        this.total = total; // 设置总条数
    }

    public T getList() {
        return list;        // 返回数据列表
    }

    public void setList(T list) { this.list = list; } // 设置数据列表
}

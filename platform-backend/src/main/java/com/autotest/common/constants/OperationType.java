package com.autotest.common.constants;

import java.util.ArrayList;
import java.util.List;

/**
 * 枚举：操作类型字典
 * 用途：定义用例步骤中可用的操作类别及其中文标签。
 */
public enum OperationType {
    BROWSER("browser", "浏览器"), // 浏览器相关操作
    SYSTEM("system", "系统"),     // 系统级操作
    PAGE("page", "网页"),         // 网页级操作
    VIEW("view", "视图"),         // 视图/界面区域操作
    RELATION("relation", "关联"), // 变量关联与传值
    ASSERTION("assertion", "断言"),// 断言校验操作
    CONDITION("condition", "条件"),// 条件分支控制
    LOOPER("looper", "循环"),     // 循环控制
    SCENARIO("scenario", "场景"); // 场景步骤封装

    /** 类型编码 */
    private final String name;
    /** 类型中文标签 */
    private final String label;

    OperationType(String name, String label) {
        this.name = name;
        this.label = label;
    }

    /**
     * 返回类型编码
     */
    @Override
    public String toString() {
        return this.name;
    }

    /**
     * 返回类型中文标签
     */
    public String toLabel(){
        return this.label;
    }

    /**
     * 按 UI 类型返回可用的操作类型编码列表
     * @param type UI 类型，例如 "web" 或其他（视图）
     * @return 该类型下可用的操作类型编码集合
     */
    public static List<String> enumList(String type){
        List<String> enumList = new ArrayList<>();
        if(type.equals("web")){
            enumList.add(BROWSER.name);
            enumList.add(PAGE.name);
        }else {
            enumList.add(SYSTEM.name);
            enumList.add(VIEW.name);
        }
        enumList.add(RELATION.name);
        enumList.add(ASSERTION.name);
        enumList.add(CONDITION.name);
        enumList.add(LOOPER.name);
        enumList.add(SCENARIO.name);
        return enumList;
    }
}

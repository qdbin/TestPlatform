package com.autotest.common.utils;

import java.util.Date;
import java.util.Random;

/**
 * 工具：字符串随机生成（simple:special）
 * 用途：生成纯字母数字或包含符号的随机串
 */
public class StringUtils {

    public final static String[] word = {
            "a", "b", "c", "d", "e", "f", "g",
            "h", "j", "k", "m", "n",
            "p", "q", "r", "s", "t",
            "u", "v", "w", "x", "y", "z",
            "A", "B", "C", "D", "E", "F", "G",
            "H", "J", "K", "M", "N",
            "P", "Q", "R", "S", "T",
            "U", "V", "W", "X", "Y", "Z"
    };

    public final static String[] num = {
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    };

    public final static String[] symbol = {
            "!", "@", "#", "$", "%", "^", "&", "*",
            "(", ")", "{", "}", "[", "]" , ".", "?", "_",
            "`", "-", ",", ";", ":", "'", "|", "~"
    };

    /**
     * 生成简单随机字符串（字母+数字）
     *
     * @param length     // 字符串长度
     * @return String    // 随机字符串
     *
     * 示例：length=6 -> "a9K2wm"
     */
    public static String randomSimpleString(int length) {
        StringBuilder stringBuffer = new StringBuilder(); // 构造结果缓冲
        Random random = new Random(new Date().getTime()); // 基于当前时间种子生成随机器
        for (int i = 0; i < length; i++) {                // 迭代生成指定长度字符
            int flag = random.nextInt(2);                 // 随机选择类型：0数字/1字母
            if (flag==0) {
                stringBuffer.append(num[random.nextInt(num.length)]);   // 追加随机数字
            } else {
                stringBuffer.append(word[random.nextInt(word.length)]); // 追加随机字母
            }
        }
        return stringBuffer.toString();                   // 返回拼接结果
    }

    /**
     * 生成复杂随机字符串（字母+数字+符号）
     *
     * @param length     // 字符串长度
     * @return String    // 随机字符串
     *
     * 示例：length=8 -> "A7@q-3_m"
     */
    public static String randomSpecialString(Integer length) {
        StringBuilder stringBuffer = new StringBuilder(); // 构造结果缓冲
        Random random = new Random(new Date().getTime()); // 基于当前时间种子生成随机器
        for (int i = 0; i < length; i++) {                // 迭代生成指定长度字符
            int flag = random.nextInt(3);                 // 随机选择类型：0字母/1数字/2符号
            switch (flag) {
                case 0:
                    stringBuffer.append(word[random.nextInt(word.length)]);      // 追加随机字母
                    break;
                case 1:
                    stringBuffer.append(num[random.nextInt(num.length)]);        // 追加随机数字
                    break;
                case 2:
                    stringBuffer.append(symbol[random.nextInt(symbol.length)]);  // 追加随机符号
                    break;
                default:
                    break;
            }
        }
        return stringBuffer.toString();                   // 返回拼接结果
    }
}

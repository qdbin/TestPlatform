/**
 * 工具方法集合（时间戳格式化、UUID、Cookie操作）
 */

/**
 * 时间戳格式化
 * @param {*} timestamp  时间戳
 */
const timestampToTime = (timestamp) => {
    let date = new Date(timestamp) // 时间值构造Date对象
    let Y = date.getFullYear() + '-'
    let M =
        (date.getMonth() + 1 < 10 ?
            '0' + (date.getMonth() + 1) :
            date.getMonth() + 1) + '-'
    let D =
        (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' '
    let h =
        (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':'
    let m =
        (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) +
        ':'
    let s =
        date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
    return Y + M + D + h + m + s
};

/** 获取UUID */
export function getUUID() {
    function S4() {
      return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1); // 随机4位16进制
    }
  
    return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4()); // 组合为标准UUID
  }  

/** 设置cookie */
function setCookie(name, value, day) {
    let date = new Date(); // 当前时间
    date.setDate(date.getDate() + day); // 过期天数
    document.cookie = name + '=' + value + ';expires=' + date; // 设置Cookie
};

/** 获取cookie */
function getCookie(name) {
    let reg = RegExp(name + '=([^;]+)'); // 匹配目标键
    let arr = document.cookie.match(reg); // 执行匹配
    if (arr) {
        return arr[1]; // 返回值
    } else {
        return ''; // 未匹配到返回空串
    }
};

/** 删除cookie */
function delCookie(name) {
    setCookie(name, null, -1); // 通过设置过期时间删除
};

/** 导出工具函数 */
export {
    timestampToTime,
    setCookie,
    getCookie,
    delCookie
}
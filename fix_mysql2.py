"""修复MySQL sql_mode - 持久化方法"""
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', database='liuma')
cursor = conn.cursor()

# 尝试使用SET PERSIST (需要MySQL 8.0)
try:
    new_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
    cursor.execute(f"SET PERSIST sql_mode = '{new_mode}'")
    print("使用 PERSIST 设置成功")
except Exception as e:
    print(f"PERSIST失败: {e}")
    # 尝试直接设置session级别
    try:
        new_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
        cursor.execute(f"SET SESSION sql_mode = '{new_mode}'")
        print("使用 SESSION 设置成功")
    except Exception as e2:
        print(f"SESSION也失败: {e2}")

conn.close()

"""修复MySQL sql_mode"""
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', database='liuma')
cursor = conn.cursor()

# 移除ONLY_FULL_GROUP_BY模式
new_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
cursor.execute(f"SET GLOBAL sql_mode = '{new_mode}'")

# 验证
cursor.execute('SHOW VARIABLES LIKE "sql_mode"')
result = cursor.fetchone()
print(f"New SQL Mode: {result}")

conn.close()
print("\n请重启MySQL服务以使更改生效")

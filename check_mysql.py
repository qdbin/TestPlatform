"""检查MySQL配置"""

import pymysql

conn = pymysql.connect(
    host="127.0.0.1", port=3306, user="root", password="123456", database="liuma"
)
cursor = conn.cursor()
cursor.execute('SHOW VARIABLES LIKE "sql_mode"')
result = cursor.fetchone()
print(f"SQL Mode: {result}")
conn.close()

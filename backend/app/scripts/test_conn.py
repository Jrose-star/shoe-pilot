import psycopg2

# 请根据你的实际情况修改这 5 个参数
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"  # 你安装时的用户名，通常是 postgres
DB_PASS = "1234"  # 比如 123456
DB_NAME = "shoepilot_db"  # 截图里的数据库名

try:
    print(f"正在尝试连接 {DB_HOST}:{DB_PORT}，数据库：{DB_NAME} ...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    print("✅ 基础连接成功！你的账号密码没问题。")
    conn.close()
except Exception as e:
    print(f"❌ 基础连接失败，详细报错如下：\n{e}")

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PG_PASSWORD = "1234"  # 注意：确认这是你安装 PG 时设置的密码

print("1. 尝试连接 PostgreSQL 默认库...")
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=PG_PASSWORD,
        host="127.0.0.1",
        port="5432",
        connect_timeout=3,  # 超过3秒连不上就报错，防止卡死
    )
    print("2. 连接成功！")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # 先查一下有没有这个库，防止重复创建报错
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='shoepilot_db'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("CREATE DATABASE shoepilot_db;")
        print("3. 数据库 shoepilot_db 创建成功！")
    else:
        print("3. 数据库 shoepilot_db 已经存在，跳过创建。")

    conn.close()

    print("4. 正在开启 pgvector 插件...")
    conn = psycopg2.connect(
        dbname="shoepilot_db",
        user="postgres",
        password=PG_PASSWORD,
        host="127.0.0.1",
        port="5432",
        connect_timeout=3,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("5. pgvector 插件开启成功！🎉 环境配置完成！")

    cursor.close()
    conn.close()
except Exception as e:
    print(f"\n❌ 出错了！错误信息: {e}")
    print("请检查：1. 密码是不是对的？ 2. PostgreSQL 服务有没有启动？")

import psycopg2

conn = psycopg2.connect(
    dbname="bookstore_db",
    user="bookstoreuser",
    password="admin",
    host="localhost",
    port=5432
)
print("连接成功")
conn.close()
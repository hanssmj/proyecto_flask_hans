import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="webapp_db"
)

cur = conn.cursor()
cur.execute("SHOW TABLES")
print("TABLAS:", cur.fetchall())

cur.close()
conn.close()
print("DB OK")

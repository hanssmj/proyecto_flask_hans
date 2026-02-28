import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "webapp_db",
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def query_one(sql, params=()):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def query_all(sql, params=()):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id

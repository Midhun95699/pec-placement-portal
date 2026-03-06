# database.py - Connects Flask to MySQL

import mysql.connector
from config import Config

def get_db():
    """Create and return a database connection"""
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Test database connection on startup"""
    conn = get_db()
    if conn:
        print("MySQL Database connected successfully!")
        conn.close()
    else:
        print(" Database connection failed!")
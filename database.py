import mysql.connector
from config import Config

def get_db():
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            port=Config.MYSQL_PORT,
            ssl_disabled=False
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_scores")
        cursor.execute("DROP TABLE IF EXISTS tasks")
        cursor.execute("DROP TABLE IF EXISTS students")
        cursor.execute("""
            CREATE TABLE students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                department VARCHAR(50) DEFAULT 'IT',
                semester INT DEFAULT 6,
                roll_no VARCHAR(20) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                title VARCHAR(200),
                topic VARCHAR(100) DEFAULT 'General',
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE test_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                topic VARCHAR(100),
                level VARCHAR(50) DEFAULT 'quick',
                score INT DEFAULT 0,
                total INT DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully!")
    else:
        print("❌ Database connection failed!")

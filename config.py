import os

class Config:
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('DB_NAME', 'pec_placement')
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'pec_placement_secret_2024')
    DEBUG = False

# config.py - All settings for your project

class Config:
    # MySQL Database settings
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'           # Your MySQL username
    MYSQL_PASSWORD = 'Midhun@09'           
    MYSQL_DATABASE = 'pec_placement'
    
    # Secret key for JWT tokens (login sessions)
    JWT_SECRET_KEY = 'pec_placement_secret_key_2024'
    
    # Flask settings
    DEBUG = True
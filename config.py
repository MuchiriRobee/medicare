"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'yourpassword'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'clinic_db'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Email Configuration (for appointment confirmations)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@medicareclinic.com'

    # Application Settings
    APPOINTMENTS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'clinic_db_dev'

class TestingConfig(Config):
    TESTING = True
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'clinic_db_test'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'clinic_db_prod'
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

# Dictionary to map config names to classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}"""
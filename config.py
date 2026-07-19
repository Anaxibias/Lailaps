import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DB = os.environ.get('POSTGRES_DB')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'D!ppy&M!16r3d43v3r'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or URL.create(
        drivername="postgresql+psycopg",
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host="db",
        port=5432,
        database=POSTGRES_DB
    )

"""FlaskのConfigを提供する"""
import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_PASSWORD = os.environ.get("DB_PASSWORD")

class DevelopmentConfig:

  # Flask
  DEBUG = True
  # SQLAlchemy
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://{user}:{password}@{host}/q_ng_db?charset=utf8'.format(**{
      'user': os.getenv('DB_USER', 'root'),
      'password': os.getenv('DB_PASSWORD', DB_PASSWORD),
      'host': os.getenv('DB_HOST', 'localhost'),
  })
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = False


Config = DevelopmentConfig
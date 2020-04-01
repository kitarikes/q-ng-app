from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask_dir.database import init_db
import flask_dir.models 

def create_app():
  app = Flask(__name__)

  app.config.from_object('flask_dir.config.Config')
  init_db(app)

  return app

app = create_app()
app.secret_key = os.environ.get("SECRET_KEY") or 'aaa'
db = SQLAlchemy(app)
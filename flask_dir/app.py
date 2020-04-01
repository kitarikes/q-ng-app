from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask_dir.database import init_db
from flask_dir.models import User, Osi, Room, Message

def create_app():
  app = Flask(__name__)

  app.config.from_object('flask_dir.config.Config')
  init_db(app)

  return app

app = create_app()
app.secret_key = os.environ.get("SECRET_KEY") or 'aaa'
db = SQLAlchemy(app)

@app.route('/')
def home():
  return render_template('home.html', s=session)

# 認証機能
@app.route('/sign_up', methods=['GET', 'POST'])
def sing_up():
  if request.method == 'GET':
    return render_template('auth/sign_up.html', s=session)
  else:
    data = request.form
    data_ = {}
    data_['username'] = data['username']
    data_['nickname'] = data['nickname']
    data_['sex'] = int(data['sex'])
    data_['grade'] = int(data['grade'])
    data_['department'] = data['department']
    data_['twitter_id'] = data['twitter_id']
    data_['comment'] = data['comment']
    data_['osi_group'] = int(data['osi_group'])
    data_['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    already_names = db.session.query(User).filter(User.username == data_['username']).all()
    if len(already_names) == 0:
      db.session.add(User(**data_))
      db.session.commit()
      return render_template('auth/finished.html', s=session)
    else:
      return 'error: already sign_upped !'

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
  if request.method == 'GET':
    return render_template('auth/sign_in.html', s=session)
  else:
    flg = False
    data = request.form
    input_name = data['username']
    input_password = data['password']
    dbnames = db.session.query(User).filter(User.username == input_name).all()
    # print(dbnames[0].password, input_password)
    if len(dbnames) != 0:
      hashed = dbnames[0].password
      if bcrypt.checkpw(input_password.encode('utf-8'),hashed.encode('utf-8')):
        flg = True

    if flg:
      session['login'] = True
      session['user_id'] = dbnames[0].id
      session['username'] = dbnames[0].username
      return redirect('/mypage/{}'.format(session['user_id']))
    else:
      return redirect('/sign_in')

@app.route('/sign_out')
def sign_out():
  del session['login']
  del session['user_id']
  del session['username']
  return redirect('/sign_in')

# profile機能
@app.route('/mypage')
def mypage_():
  if 'login' in session:
    if session['login']:
      user_id = int(session['user_id'])
      return redirect('/mypage/{}'.format(user_id))
    else:
      return redirect('/sign_in')
  else:
    return redirect('/sign_in')

@app.route('/mypage/<u_id>', methods=['GET', 'POST'])
def mypage(u_id):
  if request.method == 'GET':
    if 'login' in session:
      user_id = int(session['user_id'])
      if int(u_id) == user_id:
        user_info = db.session.query(User).filter(User.id == u_id).all()[0]
        user_info = user_info.__dict__
        del user_info['_sa_instance_state']
        del user_info['password']
        # print(user_info)
        return render_template('mypage.html', data=user_info, s=session)
      else:
        return redirect('/sign_in')
    else:
      return redirect('/sign_in')
  else:
    return 'pass'




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
group_dict = {1: '乃木坂46', 2: '欅坂46', 3: '日向坂46'}

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
    data_['adr'] = data['adr']
    pwhash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    data_['password'] = pwhash.decode('utf8')

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

        osi_li = db.session.query(Osi).filter(Osi.user_id == u_id).all()
        osi_li = [osi.__dict__ for osi in osi_li]
        # print(user_info)
        return render_template('mypage/mypage.html', data=user_info, osi=osi_li, s=session, g_dic=group_dict)
      else:
        return redirect('/sign_in')
    else:
      return redirect('/sign_in')
  else: # method POST
    return 'error: no page!!'

@app.route('/mypage/<u_id>/edit', methods=['GET', 'POST'])
def mypage_edit(u_id):
  if int(u_id) == session['user_id']:
    if request.method == 'GET':
      return render_template('mypage/edit.html', s=session)
    else:
      data = request.form
      # immutablemultidict を dict に変換
      print(data.to_dict(flat=True))
      data = data.to_dict(flat=True)
      data['group'] = int(data['group'])
      data['osi_grade'] = int(data['osi_grade'])
      osi_li = db.session.query(Osi).filter(Osi.user_id == int(u_id) , Osi.osi_grade == data  ['osi_grade']).all()
      data['user_id'] = int(session['user_id'])
      data['osi_name'] = str(data['osi_name']).replace(' ', '')
      data['osi_name'] = str(data['osi_name']).replace('　', '')
      if len(osi_li) != 0:
        db.session.query(Osi).filter(Osi.user_id == int(u_id) , Osi.osi_grade == data['osi_grade']) .delete()
      db.session.add(Osi(**data))
      db.session.commit()
      return redirect('/mypage/{}'.format(u_id))
  else:
    return "error: not enable to access your account!!"

# 検索機能
@app.route('/search', methods=['GET', 'POST'])
def search():
  if 'login' in session:
    if session['login']:
      if request.method == 'GET':
        return render_template('search/search.html', s=session)
      else:
        data = request.form
        data = data.to_dict(flat=True)
        if data['osi_name'] == '':
          del data['osi_name']
        q = db.session.query(User)
        if 'grade' in data:
          q = q.filter(User.grade == int(data['grade']))
        if 'department' in data:
          q = q.filter(User.department == data['department'])
        if 'osi_group' in data:
          q = q.filter(User.osi_group == int(data['osi_group']))
        searched_users = q.all()
        if 'osi_name' in data:
          name = str(data['osi_name']).replace(' ', '')
          name = str(name).replace('　', '')
          q_ = db.session.query(Osi).filter(Osi.osi_name == name).all()
          ids = {d.user_id for d in q_}
          all_ids = {d.id for d in q}
          n_ids = list(ids & all_ids)
          del searched_users
          searched_users = []
          for id_ in n_ids:
            searched_users.append(db.session.query(User).get(int(id_)))
        data = []
        for u in searched_users:
          u = u.__dict__
          osi1 = db.session.query(Osi).filter(Osi.user_id==int(u['id']), Osi.osi_grade==1).first()
          if osi1 != None:
            u['osi1'] = osi1.osi_name
          else:
            u['osi1'] = "設定していません"
          del u['_sa_instance_state']
          del u['password']
          data.append(u)

        #print(data)

        return render_template('search/result.html', s=session, data=data, g_dict=group_dict)

    else:
      return redirect('/sign_in')
  else:
    return redirect('/sign_in')


# db管理
@app.route('/admin/kitarikes/user-db', methods=['GET', 'POST'])
def delete():
  if request.method == 'POST':
    results = request.form.getlist('id')
    for x in results:
      db.session.query(User).filter(User.id == int(x)).delete()
      db.session.commit()
    return redirect('/admin/kitarikes/user-db')
  else:
      users = db.session.query(User).all()
      dict_ = []
      for user in users:
        d = user.__dict__
        del d['_sa_instance_state']
        del d['password']
        dict_.append(d)
      try:
        return render_template('user_db_show.html', data=dict_, s=session)
      except:
        return redirect('/sign_up')




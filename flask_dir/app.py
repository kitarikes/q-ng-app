from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from sqlalchemy import or_
import bcrypt
import os
from os.path import join, dirname
from dotenv import load_dotenv
from collections import defaultdict

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

Mobility(app)


group_dict = {1: '乃木坂46', 2: '欅坂46', 3: '日向坂46'}
user_dict = {'username':'ユーザー名','nickname':'名前', 'grade':'学年', 'osi_group':'推しグループ','comment':'自己紹介', 'department':'学部', 'sex':'性別', 'adr':'居住地', 'twitter_id': 'twitter'}
sex_dict = {1: '男', 2:'女'}

import random
@app.route('/Top')
@mobile_template('{mobile/}home.html')
def home(template):
  a = random.randint(0, 10000)  
  return render_template(template, s=session, a=a)

@app.route('/')
def index():
  return redirect('/Top')


@app.route('/usage')
def usage():
  return render_template('usage.html')

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
    data_['twitter_id'] = str(data['twitter_id']).replace('@', '')
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
      return 'このユーザー名は使われています !'

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

      osi_li = db.session.query(Osi).filter(Osi.user_id == dbnames[0].id).all()
      for osi in osi_li:
        if osi.osi_grade == 1:
          session['osi'] = osi.osi_name
          break
      else:
        session['osi'] = 'logo'



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
        return render_template('mypage/mypage.html', data=user_info, osi=osi_li, s=session, g_dic=group_dict, u_dic=user_dict, s_dic=sex_dict, notify=get_new_messages())
      else:
        return redirect('/sign_in')
    else:
      return redirect('/sign_in')
  else: # method POST
    return 'error: no page!!'

@app.route('/mypage/<u_id>/edit', methods=['POST'])
def mypage_edit(u_id):
  if int(u_id) == session['user_id']:
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
    if int(data['osi_grade']) == 1:
      session['osi'] = data['osi_name']
    if len(osi_li) != 0:
      db.session.query(Osi).filter(Osi.user_id == int(u_id) , Osi.osi_grade == data['osi_grade']) .delete()
    db.session.add(Osi(**data))
    db.session.commit()
    return redirect('/mypage/{}'.format(u_id))
  else:
    return "error: not enable to access your account!!"

@app.route('/mypage/<u_id>/profile/edit', methods=['POST'])
def profile_edit(u_id):
  if 'login' in session:
    if session['login']:
      if int(u_id) == session['user_id']:
        data = request.form
        data = data.to_dict()
        k = list(data.keys())[0]
        v = list(data.values())[0]
        if k in ['sex', 'grade', 'osi_group']:
          d = int(v)
        elif k == 'twitter_id':
          d = str(v).replace('@', '')
        else:
          d = v
        
        user = db.session.query(User).get(int(u_id))

        if k == 'nickname':
          user.nickname = v
        elif k == 'grade':
          user.grade = v
        elif k == 'department':
          user.department = v
        elif k == 'adr':
          user.adr = v
        elif k == 'sex':
          user.sex = v
        elif k == 'osi_group':
          user.osi_group = v
        elif k == 'twitter_id':
          user.twitter_id = v
        elif k == 'comment':
          user.comment = v

        db.session.commit()

        return redirect('/mypage')
    else:
      return redirect('/sign_in')
  else:
    return redirect('/sign_in')

@app.route('/mypage/r/<u_id>', methods=['GET'])
def r_mypage(u_id):
  user_info = db.session.query(User).get(int(u_id))
  user_info = user_info.__dict__
  del user_info['_sa_instance_state']
  del user_info['password']
  osi_li = db.session.query(Osi).filter(Osi.user_id == int(u_id)).all()
  osi_li = [osi.__dict__ for osi in osi_li]
  return render_template('mypage/r-mypage.html', data=user_info, osi=osi_li, s=session, g_dic=group_dict,u_dic=user_dict, s_dic=sex_dict, notify=get_new_messages())

# Message機能
@app.route('/messages/mkroom/<u_id>', methods=['GET'])
def message(u_id):
  if 'login' in session:
    if session['login']:
      my_id = session['user_id']
      o_id = int(u_id)

      data = {}
      if my_id == o_id:
        return "this is your account!! cannot send message!!"

      data['user1_id'] = my_id
      data['user2_id'] = o_id

      # 既に該当するroomがないか確認
      q_flg1 = db.session.query(Room).filter(Room.user1_id==my_id, Room.user2_id==o_id).all()
      q_flg2 = db.session.query(Room).filter(Room.user1_id==o_id, Room.user2_id==my_id).all()
      if q_flg1 == [] and q_flg2 == [] : # 無い場合のみdbに追加
        db.session.add(Room(**data))
        db.session.commit()
      q_ = db.session.query(Room)
      
      # 既にroomがある方を取得
      q = q_.filter(Room.user1_id == my_id, Room.user2_id == o_id).all() or q_.filter(Room.user1_id == o_id, Room.user2_id == my_id).all()

      q = q[0]

      return redirect('/messages/{}'.format(q.id))
    return redirect('/sign_in')
  return redirect('/sign_in')

@app.route('/messages/<r_id>', methods=['GET', 'POST'])
def get_messages(r_id):
  if 'login' in session:
    if session['login']:
      if request.method == 'GET':
        my_id = session['user_id']
        # room情報取得
        r_id = int(r_id)
        r_q = db.session.query(Room).filter(Room.id==r_id).one()
        ms = r_q.messages
        for m in ms.all():
          if m.send_user_id != my_id and m.confirm_flg == 0:
            m.confirm_flg = 1

        db.session.commit()

        #print(ms.all())
        ms_data = [[m.send_user_id, m.message] for m in ms.all()]

        # 相手の情報取得
        if r_q.user1_id == session['user_id']:
          o_id = r_q.user2_id
        else:
          o_id = r_q.user1_id
        o_q = db.session.query(User).filter(User.id==o_id).one()

        o_osi_name = get_kamiosi(o_id)

        return render_template('message/main.html', s=session, o_data=o_q, r_id=r_id, m_d=ms_data, notify=get_new_messages(), o_osi=o_osi_name)
      else: # POSTのとき
        r_id = int(r_id)
        r_q = db.session.query(Room).filter(Room.id==r_id).one()

        if session['user_id'] != r_q.user1_id and session['user_id'] != r_q.user2_id :
          return "you cannot access this account!!"
        
        m = request.form['message'] 
        
        data = {}
        data_ = {}

        data['send_user_id'] = session['user_id']
        data['message'] = m
        data['room_id'] = r_id

        data_['send_user_id'] = r_q.user2_id
        data_['message'] = m

        db.session.add(Message(**data))
        db.session.commit()
        
        return redirect('/messages/{}'.format(r_id))
    return redirect('/sign_in')
  return redirect('sign_in')

@app.route('/messages')
def message_li():
  if 'login' in session:
    if session['login']:
      my_id = session['user_id']
      r_data = []
      push_dict = defaultdict(int)

      try:
        rooms = db.session.query(Room).filter(or_(Room.user1_id==my_id, Room.user2_id==my_id)).all()

        for room in rooms:
          for m in room.messages:
            if m.send_user_id != my_id and m.confirm_flg == 0:
              push_dict[room.id] += 1
      except:
        pass

      else:
        try:
          for room in rooms:

            if room.user1_id == my_id:
              o_id = room.user2_id
            else:
              o_id = room.user1_id
            o_name = db.session.query(User).get(o_id).nickname

            d = sorted([[m.message, m.created_at] for m in room.messages], key=lambda x: x[1], reverse=True)
            if not d:
              continue
            #print(d)
            d[0][1] = d[0][1].strftime("%Y/%m/%d %H:%M")

            o_osi_name = get_kamiosi(o_id)

            r_data.append([room.id, o_name, d[0], o_osi_name])

          r_data = sorted(r_data, key=lambda x: x[2])
        except:
          return render_template('error.html', err="メッセージがありません、メッセージを送ってみましょう！", tips='/search', s=session, notify=0)
      #print(push_dict)
      #print(r_data)

      return render_template('message/list.html', r_data=r_data, s=session, push=push_dict, notify=get_new_messages())
    else:
      redirect('/sign_in')
  else:
    redirect('/sign_in')

# 検索機能
@app.route('/search', methods=['GET', 'POST'])
def search():
  if 'login' in session:
    if session['login']:
      if request.method == 'GET':
        return render_template('search/search.html', s=session, notify=get_new_messages())
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
          if u.id == session['user_id']:
            #print(u.id)
            continue
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

        return render_template('search/result.html', s=session, data=data, g_dict=group_dict, notify=get_new_messages())

    else:
      return redirect('/sign_in')
  else:
    return redirect('/sign_in')


"""
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
"""

# メッセージ通知(色変)
def get_new_messages():
  if 'login' in session:
    if session['login']:
      my_id = session['user_id']
      rooms = db.session.query(Room).filter(or_(Room.user1_id==my_id, Room.user2_id==my_id)).all()
      ans = 0
      for room in rooms:
        for m in room.messages:
          if m.send_user_id != my_id and m.confirm_flg == 0:
            ans += 1
      return ans
  return ''

# 神推し取得
def get_kamiosi(u_id):
  user = db.session.query(User).get(int(u_id))
  osi_li = user.osis
  name = 'logo'
  for osi in osi_li:
    if osi.osi_grade == 1:
      name = osi.osi_name
      break
  return name

from datetime import datetime
from flask_dir.database import db

class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True)
  password = db.Column(db.String(255))
  nickname = db.Column(db.String(30))
  sex = db.Column(db.Integer)
  grade = db.Column(db.Integer)
  department = db.Column(db.String(50))
  twitter_id = db.Column(db.String(50))
  comment = db.Column(db.String(140))
  osi_group = db.Column(db.Integer)
  adr = db.Column(db.String(50))
  #created_at = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y/%m/%d %H:%M"))
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
  #updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y/%m/%d %H:%M"), onupdate=datetime.now().strftime("%Y/%m/%d %H:%M"))
  updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
  osis = db.relationship('Osi', backref='user', lazy='dynamic', cascade='delete')


class Osi(db.Model):
  __tablename__ = 'osis'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  group = db.Column(db.Integer)
  osi_name = db.Column(db.String(50))
  osi_grade = db.Column(db.Integer)

class Room(db.Model):
  __tablename__ = 'rooms'

  id = db.Column(db.Integer, primary_key=True)
  user1_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  user2_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  messages = db.relationship('Message', backref='room', lazy='dynamic', cascade='delete')
  #created_at = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y/%m/%d %H:%M"))
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


class Message(db.Model):
  __tablename__ = 'messages'

  id = db.Column(db.Integer, primary_key=True)
  room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
  send_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  message = db.Column(db.String(600), nullable=False)
  confirm_flg = db.Column(db.Integer, default=0)
  #created_at = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y/%m/%d %H:%M"))
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


## LINK

サークル公式HP：[https://q-u46.site](https://q-u46.site)
公式twitter：[https://twitter.com/q_u_46](https://twitter.com/q_u_46)

## 使い方

[こちら](https://q-u46.site/usage)を参考にして下さい。


## 参考
- [Python3 の 定番ORM 「 SQLAlchemy 」で MySQL ・ SQLite 等を操作 – 導入からサンプルコード](https://it-engineer-lab.com/archives/1183)
- [Flask+Service Worker on Heroku で PWA チュートリアル](https://kenzo0107.hatenablog.com/entry/2018/08/14/131148)
- [flaskのssl化について](https://stackoverflow.com/questions/32237379/python-flask-redirect-to-https-from-http/50041843)
- [iconの上に通知数表示](https://stackoverflow.com/questions/49013881/materialize-css-notification-count-does-not-show-count-numbers)
- [DMのUI](https://codepen.io/andrebr/pen/xLqaKm)
- [login認証 Auth0](https://blanktar.jp/blog/2017/11/python-flask-auth0.html)
- [Git](https://qiita.com/TakumaKurosawa/items/79a75026327d8deb9c04)
- [自己紹介カード](https://deshinon.com/2019/03/03/profile-card-kopipe/)
  
```Console
$ set FLASK_APP=run.py
$ flask shell
# herokuの場合
$ heroku run FLASK_APP=run.py flask shell

>>> from flask_dir.database import db 
>>> engine = db.engine # engineメソッドを使う
>>> engine.table_names()
['alembic_version', 'messages', 'osis', 'rooms', 'users']

# table 削除
>>> from flask_dir.models import User, Osi, Room, Message
>>> Message.__table__.drop(engine)

# table 作成
>>> from flask_dir.models import User, Osi, Room, Message # import し直す
>>> Message.__table__.create(engine)
```
dynoのエラー

```Console
$ heroku ps:stop run.7454 --app q-zaka
```

clip-pathのスマホ表示エラー解決策

```
clip-path: polygon(0 0, 0% 100%, 100% 0);
-webkit-clip-path: polygon(0 0, 0% 100%, 100% 0);
```
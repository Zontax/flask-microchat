<TERMINAL RUN>
FLASK_APP=microblog.py
flask run

<db Міграція>
flask db init
<!--  команда переноса БД -->
flask db migrate -m "users table"
flask db upgrade
flask db downgrade <!-- отменяет последнюю миграции -->
flask db migrate -m "posts table"

Коли добавляємо нові колонки робим міграцію
flask db upgrade
flask db migrate -m "new fields in user model"
flask db upgrade


# is_authenticated - свойство, которое имеет значение True, если
# пользователь имеет действительные учетные данные или False в противном случае.

<Add User to db>
Вписати в термінал сайта

flask shell
from app.models import User
from app import db
u = User(username='jolygolf', email='jolygolf@example.com')
u.set_password('jolygolf')
db.session.add(u)
db.session.commit()



heroku login
heroku git:remote -a microblog-flask-test


pip install gunicorn
pip freeze > requirements.txt



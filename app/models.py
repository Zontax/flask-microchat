from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt
from app import app

# ФАЙЛ ДЛЯ РОБОТИ БД

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

rating_posts = db.Table('rating_posts',
                        db.Column('liked_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('disliked_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    '''Класс користувачів в БД'''
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), index=True, unique=True)  # Нікнейм
    username = db.Column(db.String(32), index=True, unique=True)  # Логін (для входу)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # Хеш пароля
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # Пости
    about_me = db.Column(db.String(140))  # Про мене
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # Останній сеанс

    def __repr__(self):
        return f"<Користувач: {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    ratinged_posts = db.relationship(
        'User', secondary=rating_posts,
        primaryjoin=(rating_posts.c.liked_id == id),
        secondaryjoin=(rating_posts.c.disliked_id == id),
        backref=db.backref('rating_posts', lazy='dynamic'), lazy='dynamic')

    def like(self, user):
        if not self.is_rating(user):
            self.ratinged_posts.append(user)

    def dislike(self, user):
        if self.is_rating(user):
            self.ratinged_posts.remove(user)

    def is_rating(self, user):
        return self.ratinged_posts.filter(
            rating_posts.c.liked_id == user.id).count() > 0


class Post(db.Model):
    '''Класс постів користувачів в БД'''
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"<Повідомлення: {self.body}>"

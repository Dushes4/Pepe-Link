from app import db, login_manager
from datetime import datetime
from flask_login import (LoginManager, UserMixin, login_required,
                         login_user, current_user, logout_user)
from werkzeug.security import generate_password_hash, check_password_hash


class Post(db.Model, UserMixin):
    title = db.Column(db.String(300))
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    likes = db.relationship('Like', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    is_admin = db.Column(db.Boolean, default=0)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    liked = db.relationship('Like', foreign_keys='Like.user_id', backref='user', lazy='dynamic')

    profile_data = db.relationship('Profile_data', backref='user', uselist=False)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            Like.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.post_id == post.id).count() > 0

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "{}".format(self.username)

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Profile_data(db.Model):
    gender = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    hobby = db.Column(db.String(50), nullable=False)
    contacts = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    profile_picture = db.Column(db.String(200), default='default.jpg')

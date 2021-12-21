from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Post(db.Model, UserMixin):
    title = db.Column(db.String(300))
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    picture_link = db.Column(db.String(300), nullable=False)
    likes = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.post_id


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User_auth).get(user_id)


class User_auth(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "{}".format(self.username)

    def get_id(self):
        return self.user_id


class Logged_info(object):
    def __init__(self, current_user):
        self.current_user = current_user

        if current_user.is_authenticated:
            self.logged_user = 'Авторизован  ' + str(current_user)
            self.logout_button = 'Выход'
            self.login_button = ''
            self.register_button = ''
        else:
            self.logged_user = 'Вы не авторизованы'
            self.login_button = 'Вход'
            self.logout_button = ''
            self.register_button = 'Регистрация'


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.order_by(Post.post_id.desc()).all()
    return render_template("home.html", posts=posts, logged_info=Logged_info(current_user))


@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def new_post():
    upload_message = ''
    if request.method == "POST":

        title = request.form['title']
        picture_link = request.form['picture_link']

        try:
            last_post_id = Post.query.order_by(Post.post_id.desc()).first().post_id
        except:
            last_post_id = 0

        try:
            if (requests.get(picture_link).headers['Content-Type']) in (
                    'image/gif', 'image/png', 'image/jpg', 'image/jpeg'):
                new_post_db = Post(title=title, picture_link=picture_link, user_id=1, post_id=last_post_id + 1, likes=0)
                db.session.add(new_post_db)
                db.session.commit()
                upload_message = 'Тупой мем загружен'
            else:
                upload_message = 'Ваш фаел маст би jpg png или gif. Андерстэнд?'
        except:
            upload_message = 'Ваш фаел маст би jpg png или gif. Андерстэнд?'
        return render_template("new_post.html", upload_message=upload_message)

    else:
        return render_template("new_post.html", upload_message=upload_message)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        user_to_login = db.session.query(User_auth).filter(User_auth.username == username).first()
        try:
            if user_to_login.check_password(password):
                login_user(user_to_login)
                return redirect('/home')
            else:
                message = "Wrong username or password"
        except:
            message = "Wrong username or password"

    return render_template("login.html", message=message, logged_info=Logged_info(current_user))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/home')

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        try:
            last_user_id = User_auth.query.order_by(User_auth.user_id.desc()).first().user_id

        except:
            last_user_id = 0

        try:
            if str(db.session.query(User_auth).filter(User_auth.username == username).first()) != str(username):
                new_user_db = User_auth(user_id=last_user_id + 1, username=username, email=email)
                new_user_db.set_password(password)
                db.session.add(new_user_db)
                db.session.commit()
                return redirect('/login')
            else:
                message = 'Пользователь с таким именем уже существует'
        except:
            message = 'Проверьте корректность данных'

    return render_template("register.html", message=message)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')


@app.route('/user')
@login_required
def user():
    return render_template("Profile.html")


if __name__ == "__main__":
    app.run(debug=True)

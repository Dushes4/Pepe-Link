import os
from werkzeug.utils import secure_filename
from app import app
from flask import render_template, request, redirect, url_for
from flask_login import login_required, login_user, current_user, logout_user
from .models import User, Post, Like, Profile_data, db
from .utils import *


@app.route('/')
@app.route('/home')
def home():
    logged_user = User.query.get(current_user.get_id())
    posts = Post.query.order_by(Post.id.desc()).all()
    users = User.query.order_by(User.id.desc())
    return render_template("home.html", posts=posts, users=users, logged_user=logged_user)


@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    if not User.query.get(current_user.get_id()).is_admin:
        return '<h2>Вы не обладаете правами администратора</h2><br><a href ="/home">Вернуться</a>'

    Post.query.filter_by(id=post_id).delete()
    Like.query.filter_by(post_id=post_id).delete()
    db.session.commit()
    return redirect('/home')


@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def new_post():
    logged_user = User.query.get(current_user.get_id())
    upload_message = ''
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_post_db = Post(title=title, filename=filename, user_id=current_user.get_id())
            db.session.add(new_post_db)
            db.session.commit()
            return redirect('/home')
        else:
            upload_message = 'Файл должен иметь формат png, jpg или gif'
    return render_template("new_post.html", upload_message=upload_message, logged_user=logged_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    logged_user = User.query.get(current_user.get_id())
    if current_user.is_authenticated:
        return redirect('/home')
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        user_to_login = db.session.query(User).filter(User.username == username).first()
        try:
            if user_to_login.check_password(password):
                login_user(user_to_login)
                return redirect('/home')
            else:
                message = "Неверное имя пользователя или пароль"
        except:
            message = "Неверное имя пользователя или пароль"

    return render_template("login.html", message=message, logged_user=logged_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    logged_user = User.query.get(current_user.get_id())
    if current_user.is_authenticated:
        return redirect('/home')

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        age = request.form.get('age')
        gender = request.form.get('gender')
        hobby = request.form.get('hobby')
        contacts = request.form.get('contacts')

        if username == '' or password == '' or email == '' or age == '' or hobby == '' or contacts == '':
            message = 'Проверьте корректность данных'
            return render_template("register.html", message=message)

        if str(db.session.query(User).filter(User.username == username).first()) != str(username):
            new_user_db = User(username=username, email=email)
            new_user_db.set_password(password)
            db.session.add(new_user_db)
            db.session.commit()

            new_profile_db = Profile_data(age=age, gender=gender, hobby=hobby, contacts=contacts,
                                          user_id=new_user_db.id)
            db.session.add(new_profile_db)
            db.session.commit()

            return redirect('/login')
        else:
            message = 'Пользователь с таким именем уже существует'

    return render_template("register.html", message=message, logged_user=logged_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')


@app.route('/profile_edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    logged_user = User.query.get(current_user.get_id())
    profile_data = Profile_data.query.get(current_user.get_id())
    user_data = User.query.get(current_user.get_id())
    message = ''

    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        gender = request.form.get('gender')
        hobby = request.form.get('hobby')
        contacts = request.form.get('contacts')
        profile_picture = request.files['file']

        if username == '' or age == '' or hobby == '' or contacts == '':
            message = 'Проверьте корректность данных'
            return render_template("profile_edit.html", profile_data=profile_data, user=user_data, message=message)

        if str(db.session.query(User).filter(User.username == username).first()) == str(username) and db.session.query(
                User).filter(User.username == username).first().id != current_user.get_id():
            message = 'Пользователь с таким именем уже существует'
            return render_template("profile_edit.html", profile_data=profile_data, user=user_data, message=message)

        edited_user = db.session.query(User).get(current_user.get_id())
        edited_user.username = username
        db.session.commit()

        edited_profile = db.session.query(Profile_data).get(current_user.get_id())
        edited_profile.age = age
        edited_profile.gender = gender
        edited_profile.hobby = hobby
        edited_profile.contacts = contacts

        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            edited_profile.profile_picture = filename
        db.session.commit()

        return redirect('/user/' + str(current_user.get_id()))

    return render_template("profile_edit.html", profile_data=profile_data, user=user_data, message=message,
                           logged_user=logged_user)


@app.route('/user/<int:user_id>')
@login_required
def user(user_id):
    logged_user = User.query.get(current_user.get_id())
    profile_data = Profile_data.query.get(user_id)
    user_data = User.query.get(user_id)

    show_overlap = False
    if Like.query.filter_by(user_id=current_user.get_id()).count() >= 3 and current_user.get_id() == user_id:
        show_overlap = True

    if user_data is None:
        return '<h2>Похоже, такого пользователя не существует</h2><br><a href ="/home">Вернуться</a>'
    return render_template("user.html", profile_data=profile_data, user=user_data, show_overlap=show_overlap,
                           logged_user=logged_user)


@app.route('/admin_panel', methods=['POST', 'GET'])
@login_required
def admin_panel():
    logged_user = User.query.get(current_user.get_id())
    if not User.query.get(current_user.get_id()).is_admin:
        return '<h2>Вы не обладаете правами администратора</h2><br><a href ="/home">Вернуться</a>'

    message = ''
    users = User.query.order_by(User.id.desc()).all()

    if request.method == 'POST':
        users_to_delete = ['#']
        for user_id in range(1, User.query.order_by(User.id.desc()).first().id + 1):
            if str(request.form.get('delete' + str(user_id))) == 'on':
                users_to_delete.append(user_id)

        for user_to_delete in users_to_delete:
            User.query.filter_by(id=user_to_delete).delete()
            Profile_data.query.filter_by(user_id=user_to_delete).delete()
            db.session.commit()
        message = 'Пользователи успешно удалены'

    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin_panel.html", users=users, message=message, logged_user=logged_user)


@app.route('/overlap')
@login_required
def overlap():
    logged_user = User.query.get(current_user.get_id())
    if Like.query.filter_by(user_id=current_user.get_id()).count() < 3:
        return '<h2>Вы должны лайкнуть как минимум 3 поста, чтобы получить совпадения</h2><br><a href ="/home">Вернуться</a>'
    message = ''

    users = User.query.order_by(User.id.desc()).all()
    overlaps = find_overlaps(users, current_user, Like)

    count = min([len(overlaps), 5])
    return render_template("overlap.html", message=message, overlaps=overlaps, count=count, logged_user=logged_user)




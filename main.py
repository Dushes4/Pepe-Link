from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    title = db.Column(db.String(300))
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    picture_link = db.Column(db.String(300), nullable=False)
    likes = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.post_id


class User_auth(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(64), nullable=False)


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.order_by(Post.post_id.desc()).all()
    return render_template("home.html", posts=posts)


@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    if request.method == "POST":

        title = request.form['title']
        picture_link = request.form['picture_link']

        try:
            last_post_id = Post.query.order_by(Post.post_id.desc()).first().post_id
        except:
            last_post_id = 0

        try:
            if (requests.get(picture_link).headers['Content-Type']) in ('image/gif', 'image/png', 'image/jpg', 'image/jpeg'):
                new_post_db = Post(title=title, picture_link=picture_link, user_id=1, post_id=last_post_id + 1, likes=0)
                db.session.add(new_post_db)
                db.session.commit()
            else:
                return "Error"
        except:
            return "Error"
        return redirect('/home')

    else:
        return render_template("new_post.html")


@app.route('/user')
def user():
    return render_template("Profile.html")


@app.route('/login')
def login():
    return render_template("Log-in.html")


@app.route('/register')
def register():
    return render_template("Sign-up.html")


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    picture_link = db.Column(db.String(300), nullable=False)
    likes = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.post_id


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/user/<int:user_id>')
def user():
    return render_template("user_profile.html")


@app.route('/login')
def login():
    return "Welcome to login page"


@app.route('/register')
def register():
    return "Welcome to register page"


@app.route('/new_post')
def new_post():
    return "New post creation"


if __name__ == "__main__":
    app.run(debug=True)

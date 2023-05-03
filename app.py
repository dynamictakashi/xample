from flask import Flask, render_template, request
# 乱数生成用モジュール
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/triangle', methods=['GET', 'POST'])
def janken():
    you = ""
    me = ""
    result = ""
    if request.method == 'POST':
        hand = ['グー', 'チョキ', 'パー']
        me = request.form['hand']
        you = hand[random.randint(0, 2)]
        if you == me:
            result = 'あいこ'
        elif me == 'グー' and you == 'チョキ':
            result = '勝ち'
        elif me == 'チョキ' and you == 'パー':
            result = '勝ち'
        elif me == 'パー' and you == 'グー':
            result = '勝ち'
        else:
            result = '負け'
    return render_template('triangle.html', result=result, myhand=me, cphand=you)

@app.route('/add_db')
def add_db():
    new_db = User(username='example', email='test@example.com')
    db.session.add(new_db)
    db.session.commit()
    return '追加完了'
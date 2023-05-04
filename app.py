from flask import Flask, render_template, redirect, request
# 乱数生成用モジュール
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)


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
        me = hand.index(request.form['hand'])
        you = random.randint(0, 2)
        if (me-you) % 3 == 0:
            result = 'あいこ'
        elif (me-you) % 3 == 1:
            result = '勝ち'
        else:
            result = '負け'
    return render_template('triangle.html', myhand=me, cphand=you, result=result, xhand=hand)


@app.route('/signup', methods=['GET', 'POST'])
def add_db():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        for_add = User(username=username, email=email)
        db.session.add(for_add)
        db.session.commit()
        return render_template('home.html')
    else:
        return render_template('signup.html')


@app.route('/find', methods=['GET', 'POST'])  # method"s"にする
def db_find():
    result = ""  # 最初に定義しないと動かない
    username = ""  # 最初に定義しないと動かない
    email = ""  # 最初に定義しないと動かない
    if request.method == 'POST':
        id = request.form.get('id')  # HTMLと連携、HTMLから数値取得
        found = User.query.get(id)  # 変数からDB取得
        username = found.username  # 変数からDBカラムを持ってくる
        email = found.email  # 同じくカラム持ってくる
        result = 'enable'  # ダミー用関数
        return render_template('find.html', result=result, username=username, email=email)
    else:
        return render_template('find.html')


@app.route('/sandbox', methods=['GET', 'POST'])
def jankeeen():
    if request.method == 'POST':
        opo = ""
        me = ""
        result = ""
        hand = ['グー', 'チョキ', 'パー']
        me = request.form.get('hand')
        opo = hand[random.randint(0, 2)]
        if opo == me:
            result = 'あいこ'
        elif me == 'グー' and opo == 'チョキ':
            result = '勝ち'
        elif me == 'チョキ' and opo == 'パー':
            result = '勝ち'
        elif me == 'パー' and opo == 'グー':
            result = '勝ち'
        else:
            result = '負け'
        print(result)
        print(me)
        print(opo)
        return render_template('sandbox.html')
    else:
        return render_template('sandbox.html')

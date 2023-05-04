from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from werkzeug.security import check_password_hash, generate_password_hash
# 乱数生成用モジュール
import random
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.debug = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bbs.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/triangle', methods=['GET', 'POST'])
def janken():
    if request.method == 'POST':
        hand = ['グー', 'チョキ', 'パー']
        you = random.randint(0, 2)
        me = hand.index(request.form['hand'])
        if me == you:
            result = 'あいこ'
        elif (me-you) % 3 == 2:
            result = '勝ち'
        else:
            result = '負け'
        return render_template('triangle.html', myhand=me, cphand=you, result=result, xhand=hand)
    return render_template('triangle.html')


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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            error = 'このユーザーIDは既に使用されています。'
            return render_template('signup.html', error=error)
        password_hash = generate_password_hash(password, method='sha256')
        new_user = User(user_id=user_id,password=password_hash)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

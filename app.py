from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash  # 乱数生成用モジュール
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base  # 引数"Base"の設定に必要
import datetime  # 現在時刻を投稿するためのモジュール
from sqlalchemy.orm import relationship  # 外部キー設定用のモジュール

# 初期設定用の定義
app = Flask(__name__)
app.debug = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bbs.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
Base = declarative_base()  # DBの親子関係に使用


# DB - ログインユーザー
class User(UserMixin, db.Model):
    # __tablename__で子テーブルを設定してあげる
    __tablename__ = 'user'
    # 以下は既存情報
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


# DB - ブログエントリー
class Post(db.Model):
    __tablename__ = 'post'
    # ここにFavoriteテーブルの設定を入れる

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime)

# DB - コメント


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime)

# DB - お気に入り


class Favorite(db.Model):  # 子テーブルになる、親はuserとpost
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, db.ForeignKey('user.user_id'))
    title_no = db.Column(db.Integer, db.ForeignKey('post.id'))
    title = db.Column(db.String, db.ForeignKey('post.title'))
    time = db.Column(db.DateTime)
    __table_args__ = (
        db.UniqueConstraint('name', 'title_no'),
    )


# よく使う関数

# 1.ユーザー名を取得する
def summon_user():
    setting_logged_user = current_user.get_id()  # ログインユーザーの把握
    user = User.query.get(setting_logged_user)  # レコードの取得
    summon = user.user_id
    return summon


# これはoften defに関係なし
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ベース
@app.route('/')
def index():
    base_home = True
    message = 'Hello World!'
    return render_template('home.html', base_home=base_home, title_notice=message)


# ここからページ集

# 登録
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
        new_user = User(user_id=user_id, password=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html')


# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    base_login = True
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            message = 'Welcome to World!'
            return render_template('home.html', title_notice=message)
    return render_template('login.html', base_login=base_login)


# ログアウト
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    message = 'See You!'
    return render_template('home.html', title_notice=message)


# ブログメイン画面
@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.method == 'GET':
        base_blog = True
        posts = Post.query.all()
    return render_template('blog.html', posts=posts, base_blog=base_blog)


# ブログ詳細画面
@app.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog_content(id):
    base_blog = True
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=int(id)).all()
    if request.method == 'GET':
        return render_template('blog_content.html', post=post, comments=comments, base_blog=base_blog)
    else:
        name = request.form['com_name']
        body = request.form['com_body']
        time = datetime.datetime.now()  # 時間
        # titleが30文字以上、bodyが500文字以上であるかどうかを確認する
        if len(name) == 0 or len(body) == 0:
            err_msg = "両方に文字を入力してください。"
            return render_template('blog_content.html', post=post, comments=comments, base_blog=base_blog, error=err_msg)
        elif int(30) > len(name) and 500 > len(body):
            comment = Comment(post_id=id, name=name, body=body, time=time)
            db.session.add(comment)
            db.session.commit()
            name_post = 'Thank you for Comment!'
            return render_template('home.html', post=post, comments=comments, title_notice=name_post)
        elif len(name) > 30:
            err_msg = "タイトルが長すぎるため投稿できませんでした"
            return render_template('blog_content.html', post=post, comments=comments, base_blog=base_blog, error=err_msg)
        elif len(body) > 500:
            err_msg = "内容が長すぎるため投稿できませんでした。"
            return render_template('blog_content.html', post=post, comments=comments, base_blog=base_blog, error=err_msg)
        else:
            err_msg = "投稿に失敗しました。"
            return render_template('blog_content.html', post=post, comments=comments, base_blog=base_blog, error=err_msg)


# ブログ投稿
@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def blog_post():
    base_post = True
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        time = datetime.datetime.now()  # 時間

        # titleが30文字以上、bodyが500文字以上であるかどうかを確認する
        if len(title) == 0 or len(body) == 0:
            err_msg = "両方に文字を入力してください。"
            return render_template('newpost.html', error=err_msg)
        elif int(30) > len(title) and 500 > len(body):
            posted = Post(title=title, body=body, time=time)
            db.session.add(posted)
            db.session.commit()
            title_post = 'Sucessful to Post!'
            return render_template('home.html', title_notice=title_post)
        elif len(title) > 30:
            err_msg = "タイトルが長すぎるため投稿できませんでした"
            return render_template('newpost.html', error=err_msg)
        elif len(body) > 500:
            err_msg = "内容が長すぎるため投稿できませんでした。"
            return render_template('newpost.html', error=err_msg)
        else:
            err_msg = "投稿に失敗しました。"
            return render_template('newpost.html', error=err_msg)
    return render_template('newpost.html', base_post=base_post)


# 編集
@app.route('/postedit/<int:id>', methods=['GET', 'POST'])
@login_required
def blog_edit(id):
    base_blog = True
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('postedit.html', post=post, base_blog=base_blog)
    else:
        title = request.form['title']
        body = request.form['body']
        time = datetime.datetime.now()  # 時間
        # titleが30文字以上、bodyが500文字以上であるかどうかを確認する
        if len(title) == 0 or len(body) == 0:
            err_msg = "両方に文字を入力してください。"
            return render_template('postedit.html', post=post, base_blog=base_blog, error=err_msg)
        elif int(30) > len(title) and 500 > len(body):
            posted = Post(title=title, body=body, time=time)
            db.session.add(posted)
            db.session.commit()
            title_post = 'Sucessful to Edit!'
            return render_template('home.html', title_notice=title_post)
        elif len(title) > 30:
            err_msg = "タイトルが長すぎるため投稿できませんでした"
            return render_template('postedit.html', post=post, base_blog=base_blog, error=err_msg)
        elif len(body) > 500:
            err_msg = "内容が長すぎるため投稿できませんでした。"
            return render_template('postedit.html', post=post, base_blog=base_blog, error=err_msg)
        else:
            err_msg = "投稿に失敗しました。"
            return render_template('postedit.html', post=post, base_blog=base_blog, error=err_msg)


# 削除
@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def blog_delete(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('blog'))


# お気に入り閲覧
@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite_manage():
    if request.method == 'GET':
        base_fav = True
        logged = summon_user()
        favorites = Favorite.query.filter_by(name=logged).all()
        return render_template('favorite.html', logged=logged, favorites=favorites, base_fav=base_fav)
    else:
        return redirect(url_for('/blog'))


# お気に入り追加
@app.route('/favorite/<int:id>', methods=['GET'])
@login_required
def blog_favorite(id):
    if request.method == 'GET' and current_user.is_authenticated:
        setting = current_user.get_id()  # ログインユーザーの把握
        user = User.query.get(setting)  # レコードの取得
        logged = user.user_id
        post = Post.query.get(id)  # DBを参照する
        res = Favorite.query.filter_by(name=logged, title_no=id).all()
        if res:
            return redirect(url_for('blog'))
        else:
            set1 = user.user_id
            set2 = int(post.id)
            set3 = post.title  # DBを参照する
            set4 = datetime.datetime.now()
            tsuika = Favorite(name=set1, title_no=set2, title=set3, time=set4)
            db.session.add(tsuika)
            db.session.commit()
            return redirect(url_for('blog'))

# お気に入り削除


@app.route('/favorite/delete/<int:id>', methods=['GET'])
@login_required
def favorite_delete(id):
    logged = summon_user()
    record = Favorite.query.filter_by(
        name=logged, title_no=id).first()  # レコードを取得
    if request.method == 'GET':
        db.session.delete(record)
        db.session.commit()
        return redirect('/favorite')
    else:
        return redirect('/favorite')

    '''
    #関数メモfor add fav
        base_favorite=True
        setting = current_user.get_id()  # ログインユーザーの把握
        user = User.query.get(setting)  # レコードの取得
        '''

# 昔遊びで作った機能集
# ジャンケン


@app.route('/triangle', methods=['GET', 'POST'])
@login_required
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


# DBインジェクション用
@app.route('/find', methods=['GET', 'POST'])  # method"s"にする
def db_find():
    result = ""  # 最初に定義しないと動かない
    username = ""  # 最初に定義しないと動かない
    email = ""  # 最初に定義しないと動かない
    if request.method == 'POST':
        id = request.form.get('id')  # HTMLと連携、HTMLから数値取得
        found = User.query.get(id)  # 変数からDB取得
        username = found.user_id  # 変数からDBカラムを持ってくる
        email = found.password  # 同じくカラム持ってくる
        result = 'enable'  # ダミー用関数
        return render_template('find.html', result=result, username=username, email=email)
    else:
        return render_template('find.html')


# デバッグ用
@app.route('/sandbox', methods=['GET', 'POST'])
def sunaba():
    return render_template('sandbox.html')

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
    #__tablename__で子テーブルを設定してあげる
    __tablename__ = 'user'
    #以下は既存情報
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
    #ここにFavoriteテーブルの設定を入れる

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# DB - コメント
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime)

# DB - お気に入り
class Favorite(db.Model): #子テーブルになる、親はuserとpost
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, db.ForeignKey('user.user_id'))
    title=db.Column(db.String, db.ForeignKey('post.title'))
    time = db.Column(db.DateTime)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ベース
@app.route('/')
def index():
    return render_template('home.html')


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
        username = found.username  # 変数からDBカラムを持ってくる
        email = found.email  # 同じくカラム持ってくる
        result = 'enable'  # ダミー用関数
        return render_template('find.html', result=result, username=username, email=email)
    else:
        return render_template('find.html')


# デバッグ用
@app.route('/sandbox', methods=['GET', 'POST'])
def sunaba():
    return render_template('sandbox.html')

# ここから本格的に作成する。


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
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


# ログアウト
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('home.html')


# ブログメイン画面
@app.route('/blog', methods=['GET','POST'])
def blog():
    if request.method =='GET':
        posts = Post.query.all()
        return render_template('blog.html', posts=posts)


# ブログ詳細画面
@app.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog_content(id):
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=int(id)).all()
    if request.method == 'GET':
        print(2)
        return render_template('blog_content.html', post=post, comments=comments)
    else:  # コメント機能
        name = request.form['com_name']
        body = request.form['com_body']
        time = datetime.datetime.now()  # 時間
        comment = Comment(post_id=id, name=name, body=body, time=time)
        db.session.add(comment)
        db.session.commit()
        return render_template('blog_content.html', post=post, comments=comments)


# ブログ投稿
@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def blog_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        time = datetime.datetime.now()  # 時間
        posted = Post(title=title, body=body, time=time)
        db.session.add(posted)
        db.session.commit()
    return render_template('newpost.html')


'''
DBに保存するメソッド
----
htmlで書いたものを送信する→受け取る→DBに保存
DBに保存された内容を取得する→表示する
'''


# 編集
@app.route('/postedit/<int:id>', methods=['GET', 'POST'])
@login_required
def blog_edit(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('postedit.html', post=post)
    else:
        post.title = request.form['title']
        post.body = request.form['body']
        post.time = datetime.datetime.now()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('blog'))


# 削除
@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def blog_delete(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('blog'))


# コメント投稿(統合しました)

# コメント表示(統合しました)


#お気に入り機能(ブログ一覧に移動)
@app.route('/favorite/<int:id>', methods=['GET'])
@login_required
def blog_favorite(id):
    set3=datetime.datetime.now
    if request.method =='GET' and current_user.is_authenticated:
        setting=current_user.get_id() #ログインユーザーの把握
        user=User.query.get(setting) #レコードの取得
        set1=user.user_id
        print(set1) #ログインIDを取得
        set2=Post.query.get(id) #DBを参照する
        set3=datetime.datetime.now()
        tsuika = Favorite(name=set1, title=set2.title, time=set3)
        db.session.add(tsuika)
        db.session.commit()
        return redirect('/blog')

#要は#3の記事のお気に入りを押したらユーザー2のお気に入りが追加されれば良い
#titleとusernameだけで良い。
#usernameはloginの関数使えば良い
#titleはPostからidを指定してあげれば良い
#request.query.get('カラム')


'''お気に入り機能
提案
@qpp.route('/favorites)
ログイン状態のユーザーのみが実行可能
@login_required
HTML側のボタンが押されたら、そのコメントの内容を取得してDBへ登録
/favoritesにお気に入りDBの内容を表示する
return render_template('favorites.html')
お気に入りDBはお気に入りの内容をユーザーごとに区別できるようにする
favorites = Favorite.query.filter_by(logged=user_id).all()
ユーザーのIDとお気に入りDBを紐づける（外部キーとする）
user_id:takashiが2だとして、user_id:2,記事id=5,お気に入り...

1./blog/favoritesでお気に入り一覧を閲覧できる
2.favoritesから各種お気に入りに飛べる
1=id(主キー),2=ユーザーID(外部キー),3=記事id(外部キー),4=コメントid(外部キー)

とりあえず記事のfavで運用するので…
1と2と3のみを行う。
取得すべきはユーザーidと記事id
---
取得するには・・・
DB.query.get(id)←これはidと紐づいた内容を指定する。
DB.query.filter_by().all()←filter_byで指定したものだけを抽出する。
id, user_name, entry
1 takashi 3
2 takashi 1
3 takashi 8
4 takashi 13
5 test 3
6 test 6
7 test 15
8 test 11
9 test 4

どっから引っ張ってくるかメモる
UserとPostから引っ張る。つまりUserとPostを親にする。
おそらくPostはすでに親として機能している、そこでさっきの複数外部キーを設定する必要がある。
Favテーブル作成、idと記事番号を引っ張る
コメントとユーザーを親にする

おそらくdbの設定はこれでいける
---
お次は実装
HTNL側に表示させるのはuser_idを指定するのみ。

current_user.get_id()でlogged_userのidを取得できる
ユーザー名を追加するには・・・
xxx = current_user.get_id() #idを取得
user=User.query.get(xxx) #xxxにidが入っている
user_id=user.user_id →takashi
そもそもこれをdbに登録する。だからuser.user_idで良いのでは

追加ボタンのバックエンド
postで抽出
yyy = current_user.get_id()
zzz = Post.query.get()
xxx = Favorite(id=id, user_id=yyy, post_titlepost_title)
db.session.add(xxx)
db.session.commit

postで1,takashi,これはテストきじ1です

つまり
logged_id= current_user.get_id()
xxx=Favorite.query.get(logged_id)
yyy=query.get(xxx.post_id)
render_template('favorite.html',xxx=xxx)

<td>
{{xxx.post_id}}
</td>

---
'''

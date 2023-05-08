example for a plactice that create an application by Flask.

Todo...
DB作成する
Pyに追加scr書く
htmlに追加ボタンつける
追加ボタンを押してdbに追加されるか確認
削除ボタンも追加する

DB側
class Favorite(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(ForeignKey=User.user_id)
post_title = db.Column(ForeignKey(Post.Post_title))
time = db.Column(db.DateTime)

py側
とりあえずDBを正しく呼び出す
ログインユーザーIDで抽出する


完了:
ユーザー作成,
ログイン機能,
ログアウト機能,
編集
DBその1:主題管理
DBその2:コメント管理
DBその3:ユーザー管理
DBの再構築
BBSの再実装
html修復(vh-100になってたせい)

dadadadada

未定:
ブログ機能
→作成,
削除

コメント
お気に入り
検索

おそらく全部DB経由で作成できる。

flaskを使えば割と簡単かも


お気に入り機能の構築を練ってみる

ユーザーと主題で検証

主題にファボ→DBで紐づける。

ログインAがfav→レコードが登録される。
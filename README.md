example for a plactice that create an application by Flask.
Todo...
DBの再構築
BBSの再実装
ログイン機能の再実装
DBその1:主題管理
DBその2:コメント管理
DBその3:ユーザー管理

ユーザー作成x
ログイン機能x
ログアウト機能x
ブログ機能
→作成
→編集
→削除
おそらく全部DB経由で作成できる。
flaskを使えば割と簡単かも

コメント
お気に入り
検索

お気に入り機能の構築を練ってみる
ユーザーと主題で検証
主題にファボ→DBで紐づける。

ログインAがfav→レコードが登録される。

ファボ投稿→ファボポストの順番らしい
1:テスト投稿です
1,1
1,4
1,8
1,10
1,15

2,3
2,4
2,8
2,10
2,15
ログイン/ログアウト実装ずみ、学習が曖昧
ブログ機能
コメント機能
ファボ機能
検索機能

fav作成
ログイン状態でのみ機能する
fav押す→ファボDBに外部キーのきじIDとコメントidが表示される
if favあり→ボタンがdisable

@app.route('<int:id>/favs')
def fav表示
db.query.get()
return render_template('fav.html',entry=entry,comment=comment)
'''

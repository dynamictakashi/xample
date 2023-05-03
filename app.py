from flask import Flask, render_template, request
#乱数生成用モジュール
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/triangle', methods=['GET', 'POST'])
def janken():
    result = ""
    selected_hand = ""
    computer_hand = ""
    if request.method == 'POST':
        # HTMLフォームから送信されたデータを取得
        selected_hand = request.form['hand']
        # コンピュータの手をランダムに決定
        hands = ["グー", "チョキ", "パー"]
        #リスト+randintを用いてhandsの中身をランダム出力できるようにします。
        computer_hand = hands[random.randint(0,2)]
        
        # 勝敗の判定 1=チョキ, 2=パー,0=グー
        if selected_hand == "グー" and computer_hand == "チョキ":
            result = "勝ち"
        elif selected_hand == "チョキ" and computer_hand == "パー":
            result = "勝ち"
        elif selected_hand == "パー" and computer_hand == "グー":
            result = "勝ち"
        elif selected_hand == computer_hand:
            result = "引き分け"
        else:
            result = "負け"
    #レンダーテンプレートに表示したい変数を渡してあげましょう。
    return render_template('triangle.html', result=result,myhand=selected_hand,cphand=computer_hand)


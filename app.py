from flask import Flask, render_template, request
#乱数生成用モジュール
from random import randint

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
    if request.method == 'POST':
        # HTMLフォームから送信されたデータを取得
        selected_hand = request.form['hand']
        
        # コンピュータの手をランダムに決定
        hands = ["グー", "チョキ", "パー"]
        computer_hand = randint(0, 2)
        
        # 勝敗の判定
        if selected_hand == "グー" and computer_hand == 1:
            result = "勝ち"
        elif selected_hand == "チョキ" and computer_hand == 2:
            result = "勝ち"
        elif selected_hand == "パー" and computer_hand == 0:
            result = "勝ち"
        elif selected_hand == hands[computer_hand]:
            result = "引き分け"
        else:
            result = "負け"
            print(computer_hand, selected_hand)
    
    return render_template('triangle.html', result=result)


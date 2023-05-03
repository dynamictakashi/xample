from flask import Flask, render_template, request
# 乱数生成用モジュール
import random


app = Flask(__name__)
app.debug = True
app.config['DEBUG'] = True


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

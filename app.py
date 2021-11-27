from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/stt.html',methods=['GET','POST'])
def stt():  # put application's code here
    return render_template('stt.html')


@app.route('/ml.html',methods=['GET','POST'])
def ml():  # put application's code here
    return render_template('ml.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

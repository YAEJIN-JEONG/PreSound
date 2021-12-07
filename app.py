import ssl

import requests
from bs4 import BeautifulSoup

from feature_extraction.makefeat import featureextract

import os
import sys
import numpy as np

from keras.models import load_model
from werkzeug.utils import secure_filename
from utilss.utils import process_predictions
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template

app = Flask(__name__,static_url_path='/static')


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/stt', methods=['GET', 'POST'])
def stt():  # put application's code here
    return render_template('stt.html')

@app.route('/news', methods=['GET','POST'])
def news():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.fnnews.com/search?search_txt=청각장애인&page=0', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    news = soup.select('#root > div.contents > div > div.wrap_left > div.wrap_artlist.mt20 > div.inner_artlist > ul > li')
    news_dict={}
    for i in range(9):
        for new in news:
            a_tag = new.select_one('a')
            if a_tag is not None:
                url='https://www.fnnews.com'
                url+=new.select_one('a:nth-child(1)')['href']
                image = new.select_one('a:nth-child(1) > span > img')['src']
                title = a_tag.select_one('strong').text.strip()
                desc = new.select_one('a:nth-child(2) > p').text.strip()
                date = new.select_one('em').text
                news_dict[str(url)]={
                    'img':image,
                    'title':title,
                    'desc':desc,
                    'date':date
                }
                print('크롤링 완료')

    return render_template('news.html',news_dict=news_dict)


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'opus'}


# Limit content size
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_features(filepath):
    feature_extractor = featureextract('config_files/feature_extraction.json')
    return feature_extractor.extract_features(filepath)


# Upload files function
@app.route('/ml', methods=['GET', 'POST'])
def ml():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']  # 소리 받은거
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filename)
            return redirect(url_for('classify_and_show_results', filename=filename))
    return render_template("ml.html")


# Classify and show results
@app.route('/results', methods=['GET'])
def classify_and_show_results():
    filename = request.args['filename']
    # Compute audio signal features
    features = extract_features(filename)
    features = np.expand_dims(features, 0)
    # Load model and perform inference
    model = load_model('models/best_model.hdf5')
    predictions = model.predict(features)[0]
    # Process predictions and render results
    predictions_probability, prediction_classes = process_predictions(predictions,
                                                                    'config_files/classes.json')

    predictions_to_render = {prediction_classes[i]:"{}%".format(
                                round(predictions_probability[i]*100, 3)) for i in range(3)}
    # Delete uploaded file
    os.remove(filename)
    # Render results
    return render_template("results.html",
        filename=filename,
        predictions_to_render=predictions_to_render)


if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password='louie')
    app.run(host="0.0.0.0", port=5000, ssl_context=ssl_context)

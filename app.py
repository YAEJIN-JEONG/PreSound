from flask import Flask, render_template, request
import ssl
import requests, crawling
from bs4 import BeautifulSoup

app = Flask(__name__,static_url_path='/static')


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/stt.html', methods=['GET', 'POST'])
def stt():  # put application's code here
    return render_template('stt.html')


@app.route('/ml.html', methods=['GET', 'POST'])
def ml():
    # put application's code here
    return render_template('ml.html')


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


if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password='louie')
    app.run(host="0.0.0.0", port=5000, ssl_context=ssl_context)


from flask import Flask, request, render_template
from get_txt_from_url import get_txt_from_url
import json
import requests
import os

app = Flask(__name__)

# .env ファイルから環境変数を読み込む
from dotenv import load_dotenv
load_dotenv()

# 環境変数を取得
endpoints = os.environ.get("ENDPOINTS")

if endpoints is None:
    raise EnvironmentError("The ENDPOINTS environment variable is not set.")
else:
    endpoints = endpoints.split(',')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', endpoints=endpoints)

def fetch_content(url, endpoint):
    if endpoint == "http://127.0.0.1:5000/get_txt_from_url":
        return json.loads(get_txt_from_url(type('FakeRequest', (), {'args': {'url': url}}))[0])['content']
    else:
        response = requests.get(f"{endpoint}?url={url}")
        return json.loads(response.text)['content'] if response.status_code == 200 else f"Error: {response.text}"

@app.route('/show_result', methods=['POST'])
def show_result():
    url = request.form['url']
    endpoint = request.form['endpoint']
    content = fetch_content(url, endpoint)
    return render_template('index.html', content=content, endpoints=endpoints)

@app.route('/get_txt_from_url', methods=['GET'])
def get_txt_from_url_route():
    return get_txt_from_url(request)

if __name__ == "__main__":
    app.run(debug=True)
from pymongo import MongoClient
import jwt
import datetime
import hashlib
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta




app = Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://anwjsrlrhwkd:spa0000@cluster0.imdsh.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.WebMiniProject

# 서버 기능 구현
def get_wishlist():
    # 네이버 API 설정
    client_id = "coSd7QD9SiS6WMyg3bx2"
    client_secret = "gm90HNggug"
    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}

    display = "20"
    query = "아이패드 11"
    api_url = "https://openapi.naver.com/v1/search/shop.json?query="+query+"&display="+display

    r = requests.get(api_url, headers=headers)
    response = r.json()

    for data in response["items"]:
        print(data['title'][:30])
        print(data["lprice"], "원")




# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)

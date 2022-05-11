from pymongo import MongoClient
import jwt
import datetime
import hashlib
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import re




app = Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://anwjsrlrhwkd:spa0000@cluster0.imdsh.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.WebMiniProject

# 서버 기능 구현

# html 태그 제거
def remove_tag(string):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', string)
    return cleantext

# 상품정보 저장
def get_wishlist(query):
    # 네이버 API 설정
    client_id = "coSd7QD9SiS6WMyg3bx2"
    client_secret = "gm90HNggug"
    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}

    display = "1"
    api_url = "https://openapi.naver.com/v1/search/shop.json?query="+query+"&display="+display

    r = requests.get(api_url, headers=headers)
    response = r.json()
    data = response["items"]

    name = remove_tag(data['title'])
    img_url = data["image"]
    price = data["lprice"]+" 원"

    return name, img_url, price

# 임시
@app.route('/', methods=['GET'])
def get():
    return render_template("mywishlist.html")

@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})

        name, img_url, price = get_wishlist(request.form["product_give"])
        date_receive = request.form["date_give"]
        is_public_receive = request.form["is_public"]

        doc = {
            "user_id": user_info["user_id"],
            "name": name,
            "img_url": img_url,
            "price": price,
            "upload_date": date_receive,
            "purchashed": False,
            "deleted": False,
            "public": is_public_receive
        }
        db.product.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)

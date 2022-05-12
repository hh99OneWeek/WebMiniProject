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
db_url = "mongodb+srv://anwjsrlrhwkd:spa0000@cluster0.da3km.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(db_url)
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
    data = response["items"][0]

    name = remove_tag(data['title'])
    img_url = data["image"]
    price = int(data["lprice"])

    return name, img_url, price


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
            "public": is_public_receive == "true"
        }
        db.products.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")

        if username_receive == "":
            products = list(db.products.find({}).sort("date", -1).limit(20))
        else:
            products = list(db.products.find({"username": username_receive}).sort("date", -1).limit(20))

        for product in products:
            product["_id"] = str(product["_id"])
            product["likes"] = db.likes.count_documents({"prod_id": product["_id"]})
            product["likes_by_me"] = bool(
                db.likes.find_one({"prod_id": product["_id"], "user_id": payload['id']}))

        products.sort(key= lambda product: product["price"])
        print(products)

        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "products": products})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"user_id": username}, {"_id": False})
        return render_template('mywishlist.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        prod_id_receive = request.form["prod_id_give"]
        action_receive = request.form["action_give"]
        doc = {
            "prod_id": prod_id_receive,
            "user_id": user_info["user_id"],
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)

        count = db.likes.count_documents({"prod_id": prod_id_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# login.html
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        # return render_template('index.html', user_info=user_info)
        return render_template('mywishlist.html', user_info=user_info, status=True)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': username_receive, 'pwd': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": username_receive,  # 아이디
        "pwd": password_hash,  # 비밀번호
        "nick": username_receive,  # 프로필 이름 기본값은 아이디
        "img": "",  # 프로필 사진 파일 이름
        "img_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "description": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"user_id": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# profile.html
@app.route('/profile/<username>')
def profile(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"user_id": username}, {"_id": False})


        return render_template('profile.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        address_receive = request.form["address_give"]
        phone_number_receive = request.form["phone_number_give"]
        age_receive = request.form["age_give"]
        dream_receive = request.form["dream_give"]
        hobby_receive = request.form["hobby_give"]
        email_receive = request.form["email_give"]


        new_doc = {
            "nick": name_receive,
            "description": about_receive,
            "address": address_receive,
            "phone_number": phone_number_receive,
            "age": age_receive,
            "dream": dream_receive,
            "hobby": hobby_receive,
            "email": email_receive,
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            print("+++++++")
            img_realname = file.filename.split(".")[0] +'.' +file.filename.split(".")[1]
            print(img_realname)
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/"+file_path)
            new_doc["img"] = filename
            new_doc["img_real"] = file_path

        db.users.update_one({'user_id': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)

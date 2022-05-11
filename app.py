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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

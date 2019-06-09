import redis
from flask import Flask
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from config import My_config

app = Flask(__name__)

CSRFProtect(app)
Session(app)
app.config.from_object(My_config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=My_config.REDIS_HOST, port=My_config.REDIS_PORT)
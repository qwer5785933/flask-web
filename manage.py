from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# from config import My_config


app = Flask(__name__)
#
class My_config(object):
     DEBUG=True
     SQLALCHEMY_DATABASE_URI='mysql://python:mysql@127.0.0.1:3306/flask_programe'
     SQLALCHEMY_TRACK_MODIFICATIONS=False
     REDIS_HOST = "127.0.0.1"
     REDIS_PORT = 6379
#
     SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
     # flask_session的配置信息
     SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
     SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
     SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
     PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

CSRFProtect(app)
Session(app)
app.config.from_object(My_config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=My_config.REDIS_HOST, port=My_config.REDIS_PORT)


manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()

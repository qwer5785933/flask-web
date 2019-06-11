from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from config import *


db=SQLAlchemy()
# redis_store=None #type:StrictRedis
redis_store = None  # type:StrictRedis
#
# redis_store: StrictRedis = None


def set_up_log(u_selected_config):
    # 设置日志的记录等级
    logging.basicConfig(level=seleceted_config[u_selected_config].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)





def create_app(u_selected_config):
    app = Flask(__name__)
    set_up_log(u_selected_config)
    CSRFProtect(app)
    Session(app)

    app.config.from_object(seleceted_config[u_selected_config])

    db.init_app(app)
    # db = SQLAlchemy(app)
    global redis_store

    redis_store = redis.StrictRedis(host=My_config.REDIS_HOST, port=My_config.REDIS_PORT)
    from info.moduls.index import index_
    from info.moduls.passport import passport_

    app.register_blueprint(index_)
    app.register_blueprint(passport_)
    return app



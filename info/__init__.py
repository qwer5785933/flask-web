from logging.handlers import RotatingFileHandler

import redis
from flask import Flask, app, jsonify
from flask import g
from flask import render_template
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask.ext.wtf.csrf import generate_csrf

from config import *


db=SQLAlchemy()
from info.utils.common import do_index_class, check_user

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


    app.config.from_object(seleceted_config[u_selected_config])
    app.add_template_filter(do_index_class,"indexClass")
    @app.after_request
    def after_request(response):
        # 调用函数生成 csrf_token
        csrf_token = generate_csrf()
        # 通过 cookie 将值传给前端
        response.set_cookie("csrf_token", csrf_token)
        return response


    CSRFProtect(app)
    Session(app)

    db.init_app(app)
    # db = SQLAlchemy(app)
    # @app.errorhandler(404)
    # @check_user
    # def page_notfound(e):
    #     user=g.user
    #     data={
    #         'user':user.to_dict()
    #     }
    #     return render_template('others/404.html',data=data)




    global redis_store

    redis_store = redis.StrictRedis(host=My_config.REDIS_HOST, port=My_config.REDIS_PORT)
    from info.moduls.index import index_
    from info.moduls.passport import passport_
    from info.moduls.news import news_blu
    from info.moduls.profile import profile_blu
    from info.moduls.admin import admin_blu


    app.register_blueprint(profile_blu)
    app.register_blueprint(index_)
    app.register_blueprint(passport_)
    app.register_blueprint(news_blu)
    app.register_blueprint(admin_blu)
    return app




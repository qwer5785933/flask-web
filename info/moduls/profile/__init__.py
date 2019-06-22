from flask import Blueprint
from flask.ext.wtf.csrf import generate_csrf

profile_blu=Blueprint("profile", __name__, url_prefix='/user')

from . import views




# @profile_blu.after_request
# def after_request(response):
#     # 调用函数生成 csrf_token
#     csrf_token = generate_csrf()
#     # 通过 cookie 将值传给前端
#     response.set_cookie("csrf_token", csrf_token)
#     return response
# @profile_blu.before_request
# def set_csrf(response):
#     csrf_token=generate_csrf()
#     response.set_cookie()
#     return response
import random
import re
from datetime import datetime

import redis
from flask import abort
from flask import current_app, jsonify
from flask import json
from flask import logging
from flask import make_response

from flask import request
from flask import session

from info import constants, db
from info import redis_store
from info.constants import SMS_CODE_REDIS_EXPIRES
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.moduls.passport import passport_
from info.utils.captcha import captcha
from info.utils.response_code import RET






@passport_.route('/')
def passport():
    return 'where is U 后缀，大兄弟'

@passport_.route('/image_code')
def get_image_code():
    # 后台生成图片验证码，并把验证码文字内容当作值，验证码编号当作key存储在 redis 中
    # 后台把验证码图片当作响应返回给前端
    # 前端申请发送短信验证码的时候带上第1步验证码编号和用户输入的验证码内容
    # 后台取出验证码编号对应的验证码内容与前端传过来的验证码内容进行对比
    # 如果一样，则向指定手机发送验证码，如果不一样，则返回验证码错误

    # a=request.args.get('code_id',None)
    # 前端页生成验证码编号，并将编号并提交到后台去请求验证码图片
    imageCodeId=request.args.get('imageCodeId',None)
    # print(imageCodeId)
    # print(current_app.config.SESSION_REDIS)不能用app.config点出来
    if not imageCodeId:
        return abort(403)

    name,text,image=captcha.captcha.generate_captcha()


    try:
        redis_store.setex('imageCodeId'+imageCodeId,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        # print(redis_store.get(('imageCodeId'+imageCodeId).encode()))

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    return image


@passport_.route('/sms_code',methods=['POST'])
def send_sms():
    msg_json=request.json
    mobile=msg_json.get('mobile')
    image_code=msg_json.get('image_code')
    image_code_id=msg_json.get('image_code_id')
    # print([mobile,image_code,image_code_id])

    if not all([mobile,image_code,image_code_id]):
        current_app.logger.error('参数有误')
        return jsonify(errno=RET.PARAMERR,errmsg='参数有误')

    if not re.match('1[35678]\d{9}',mobile):
        current_app.logger.error('手机号不正确')
        return jsonify(errno=RET.PARAMERR, errmsg='手机号不正确')

    try:

        real_img_code=redis_store.get('imageCodeId'+image_code_id)

    except Exception as e:
        print(e)

    if not real_img_code:
        current_app.logger.error('验证码在数据库里面读取不到')
        return jsonify(errno=RET.PARAMERR, errmsg='验证码在数据库里面读取不到')

    if real_img_code.lower().decode()!=image_code.lower():
        print(real_img_code.lower().decode())
        print(image_code.lower())
        current_app.logger.error('验证码输入错误')
        return jsonify(errno=RET.PARAMERR, errmsg='验证码输入错误')

    #生成随机数
    phone_passport='%06d'%random.randint(0,999999)
    print(phone_passport)

    # ccp = CCP()
    # # 注意： 测试的短信模板编号为1
    # phone_send_status=ccp.send_template_sms('17681608630', [phone_passport, 5], 1)
    phone_send_status=0

    if phone_send_status == -1:
        current_app.logger.error('云通讯发送失败')
        return jsonify(errno=RET.THIRDERR, errmsg='云通讯发送失败')

    if phone_send_status ==0:
        try:
            phone_passport_set=redis_store.set(mobile,phone_passport,SMS_CODE_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.IOERR, errmsg='写入短信验证码错误')


    return jsonify(errno=RET.OK, errmsg="发送成功")



@passport_.route('/register',methods=['POST'])
def register():
    submit_request=request.json
    password=submit_request.get('password')
    mobile=submit_request.get('mobile')
    smscode=submit_request.get('smscode')
    print([password, mobile, smscode])

    if not all([password,mobile,smscode]):
        current_app.logger.error('数据没有获取完整')
        return jsonify(errno=RET.NODATA, errmsg='数据没有获取完整')

    # if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z_]{8,16}$',password):
    #     current_app.logger.error('密码格式不对')
    #     return jsonify(errno=RET.RET.PARAMERR, errmsg='密码格式不对')

    try:
        real_smscode=redis_store.get('mobile')
    except Exception as e:
        current_app.logger.error(e)
        current_app.logger.error('数据库查询错误')
        return jsonify(errno=RET.DBERR,errmsg='数据库查询错误')

    # if real_smscode!=smscode:
    #     current_app.logger.error('密码格式不对')
    #     return jsonify(errno=RET.PARAMERR, errmsg='密码格式不对')

    user=User()
    user.mobile=mobile
    user.nick_name=mobile
    user.last_login=datetime.now()
    print(user.last_login)
    user.password=password
    # user.password_hash=password.__hash__()
    # print(password)







    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        current_app.logger.error(e)
        current_app.logger.error('数据提交错误')
        db.session.rollback()
        return jsonify(errno=RET.DATAEXIST, errmsg='密码保存到mysql失败')
    # print(current_app.config.SECRET_KEY)
    current_app.config.secret_key='1234'
    session['user_id']=user.id
    session['mobile']=user.mobile
    session['nick_name']=user.id
    print('注册成功')
    return jsonify(errno=RET.OK, errmsg="发送成功")

    # URL： / passport / login
    # 请求方式：POST
    # 传入参数：JSON格式
    # 参数
@passport_.route('/login',methods=['POST'])
def login():
    req_obj=request.json
    password=req_obj.get('passport')
    mobile=req_obj.get('mobile')
    print([password,mobile])

    if not all([password,mobile]):
        return jsonify(errno=RET.DATAERR,errmsg='数据缺少')

    try:
        user_select=User.query.filter_by(mobile=mobile).first()

    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DATAERR,errmsg='数据库查询失败')

    if not user_select:
        return jsonify(errno=RET.DATAERR,errmsg='数据库查询不到')

    if  not user_select.check_password(password):
        return jsonify(errno=RET.DATAERR,errmsg='用户名或者密码错误')

    session['user_id']=user_select.id
    session['nick_name']=user_select.nick_name
    session["mobile"] = user_select.mobile
    print(session["mobile"])

    print('登录成功')

    return jsonify(errno=RET.OK,errmsg='OK')

@passport_.route('/logout',methods=['GET'])
def logout():
    print(1)
    # mobile = request.args.get('mobile')
    # password = request.args.get('password')
    session.pop('mobile',None)
    session.pop('user_id',None)
    session.pop('nick_name',None)
    #
    # if not all([mobile, password]):
    #     return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    return jsonify(errno=RET.OK, errmsg='OK')









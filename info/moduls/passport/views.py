import redis
from flask import abort
from flask import current_app, jsonify
from flask import make_response

from flask import request
from flask import session

from info import constants
from info import redis_store
from info.utils.captcha import captcha
from info.utils.response_code import RET
from . import passport_




@passport_.route('/')
def passport():
    return 'success'

@passport_.route('/get_image_code')
def get_image_code():
    # 后台生成图片验证码，并把验证码文字内容当作值，验证码编号当作key存储在 redis 中
    # 后台把验证码图片当作响应返回给前端
    # 前端申请发送短信验证码的时候带上第1步验证码编号和用户输入的验证码内容
    # 后台取出验证码编号对应的验证码内容与前端传过来的验证码内容进行对比
    # 如果一样，则向指定手机发送验证码，如果不一样，则返回验证码错误

    # a=request.args.get('code_id',None)
    # 前端页生成验证码编号，并将编号并提交到后台去请求验证码图片
    imageCodeId=request.args.get('code_id',None)
    # print(imageCodeId)
    # print(current_app.config.SESSION_REDIS)不能用app.config点出来
    if not imageCodeId:
        return abort(403)

    name,text,image=captcha.captcha.generate_captcha()


    try:
        redis_store.setex('imageCodeId'+imageCodeId,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        print(redis_store.get(('imageCodeId'+imageCodeId).encode()))

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    return image


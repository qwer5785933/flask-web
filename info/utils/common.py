import functools

from flask import current_app
from flask import g
from flask import session

from info.models import User


def do_index_class(eum_id):
    if eum_id==0:
        return 'first'
    elif eum_id==1:
        return 'second'
    elif eum_id==2:
        return 'third'
    else:
        return ''



def check_user(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            # 尝试查询用户的模型
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 把查询出来的数据赋值给g变量
        g.user = user
        return f(*args, **kwargs)
    return wrapper



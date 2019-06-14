from flask import current_app, jsonify
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import redis_store
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_

@index_.route('/')
def hello_world():
    # redis_store.set('name','laowang')
    # print(redis_store.get('name').decode())
    user_id = session.get("user_id", None)
    user = None
    if user_id:
        # 尝试查询用户的模型
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 右侧的新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个空的字典列表，里面装的就是字典
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询分类数据，通过模板的形式渲染出来
    # categories = Category.query.all()
    #
    # category_li = []
    # for category in categories:
    #     category_li.append(category.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        # "category_li": category_li
    }

    return render_template('news/index.html', data = data)






@index_.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')





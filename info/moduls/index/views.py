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
    user_id=session.get('user_id',None)
    user=None
    if user_id:
        try:
            user=User.query.get(user_id)

        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库查询错误User')


    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误News')
    click_news_list=[]
    for news in news_list:
        news_dict=news.to_dict()
        click_news_list.append(news_dict)


    try:
        categories=Category.query.all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询错误Categories')

    categorie_list=[]
    for category in categories:

        categorie_list.append(category.to_dict())




    data={
        'user':user.to_dict() if user else None,
        'news_dict_li':click_news_list,
        'categories':categorie_list
    }
    return render_template('news/index.html',data=data)



@index_.route('/news_list')
def news_list():
    # res = request.json
    cid = request.args.get('cid',1)
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)

    # if not all([res,cid,per_page]):
    #     return jsonify(errno=RET.PARAMERR,errmsg='缺少页码参数')
    #
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)

    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')

    news_list = []
    if cid!=1:
        news_list.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*news_list).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    news_model_list = paginate.items  # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    # 将模型对象列表转成字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_dict_li
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)







@index_.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')





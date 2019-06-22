from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info import check_user, db
from info import constants
from info.models import User, News, Category
from info.utils.captcha.image_storage import storage
from info.utils.response_code import RET
from . import profile_blu



@profile_blu.route('/news_list')
@check_user
def news_list():
    user=g.user
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg="用户未登录")
    page = request.args.get('page', 1)

    try:
        pagination=News.query.filter(News.user_id==user.id). \
            paginate(page,constants.OTHER_NEWS_PAGE_MAX_COUNT,False)
        news_list = pagination.items

        total_page = pagination.pages
        news_dict_li = news_list
        current_page = pagination.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")


    data = {"news_list": news_dict_li,
            "total_page": total_page,
            "current_page": current_page}
    return render_template('news/user_news_list.html', data=data)


@profile_blu.route('/news_release',methods=['POST','GET'])
@check_user
def news_release():
    user=g.user
    if request.method=='GET':
        category=Category.query.all()

        categories=[]
        for ca in category:
            categories.append(ca.to_dict())

        categories.pop(0)
        data={
            'categories':categories
        }

        return render_template('news/user_news_release.html',data=data)
    if request.method=='POST':
        title=request.form.get('title')
        category=request.form.get('category_id',2)
        digest=request.form.get('digest')
        source = '个人发布'
        index_image=request.files.get('index_image')
        content=request.form.get('content')
        if not all([title,category,category,content]):
            return jsonify(errno=RET.PARAMERR, errmsg='除了图片都要')
        try:
            news=News()
            news.title=title
            news.category_id=category
            news.source = source
            news.digest=digest
            news.content=content
            news.index_image_url=""
            news.status=1
            news.user_id=user.id
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='创建数据失败')
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='创建数据失败')

        # data={
        #     'news':news.to_dict(),
        #     'user':user.to_dict if user else  None
        # }

        return jsonify(errno=RET.OK,errmsg='yyyy')



@profile_blu.route('/collection')
@check_user
def user_collection():
    user=g.user
    page=request.args.get('p',1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    my_collection_news=user.collection_news.paginate(page,constants.USER_FOLLOWED_MAX_COUNT,False)
    current_page=my_collection_news.page
    total_page=my_collection_news.pages
    newslist=my_collection_news.items
    data={
        'collections':newslist,
        'current_page':current_page,
        'total_page':total_page
    }
    return render_template('news/user_collection.html',data=data)





@profile_blu.route('/pass_info', methods=["GET", "POST"])
@check_user
def pass_info():
    if request.method == "GET":
        return render_template('news/user_pass_info.html')

    # 1. 获取到传入参数
    data_dict = request.json
    old_password = data_dict.get("old_password")
    new_password = data_dict.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2. 获取当前登录用户的信息
    user = g.user

    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 更新数据
    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")



# 上传图片
@profile_blu.route('/pic_info',methods=['POST','GET'])
@check_user
def pic_info():
    user=g.user
    if request.method=='GET':
        data={
            'user':user.to_dict() if user else None
        }
        return render_template('news/user_pic_info.html',data=data)

    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")
    try:
        print('qiniu...')
        avatar_url=storage(avatar_file)
        print('qiniu ok')
    except Exception as e:
        return jsonify(errno=RET.THIRDERR, errmsg="第三方系统错误")
    user.avatar_url=avatar_url

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="第三方系统错误")

    data={
        'avatar_url':user.to_dict()
    }
    return jsonify(errno=RET.OK,errmsg='OK')
    # request.json.get('avatar_url')
    # request.json.get('avatar_url')


#用户资料修改
@profile_blu.route("/base_info",methods=['POST','GET'])
@check_user
def user_base_info():
    print(request.method)
    user=g.user
    if request.method=='POST':
        gender=request.json.get('gender')
        nick_name=request.json.get('nick_name')
        signature=request.json.get('signature')

        if gender not in['MAN','WOMAN']:
            return jsonify(errno=RET.PARAMERR,errmsg='gender参数错误')


        if not all([signature,nick_name,gender]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不全')


        user.gender=gender
        user.nick_name=nick_name
        user.signature=signature
        try:
            db.session.add(user)
            db.session.commit()

        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='数据库提交失败')

        session['nick_name']=nick_name
        return jsonify(errno=RET.OK,errmsg='ok')

    return render_template("news/user_base_info.html")



@profile_blu.route('/info')
@check_user
def user_info():
    user=g.user
    if not user:
        return redirect('/')
    data={
        'user':user.to_dict() if user else None
    }

    return render_template('news/user.html', data=data)

# @user_info_blu.route('')
# def modify_password():
#     pass
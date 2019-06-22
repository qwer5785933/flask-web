import time
from datetime import datetime, timedelta

from flask import current_app, jsonify
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from info import check_user, db
from info import constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import admin_blu

@admin_blu.route('/login',methods=['POST','GET'])
@check_user
def admin_login():
    user=g.user
    if request.method=='GET':
        return render_template('admin/login.html')
    if request.method=='POST':
        password=request.form.get('password')
        name=request.form.get('username')
        if not all([password,name]):
            return render_template('admin/login.html')
        try:
            user=User.query.filter(User.mobile==name,user.is_admin==True).first()
        except Exception as e:
            current_app.logger.error(e)

        if not user:
            return render_template('admin/login.html')

        password_checked=user.check_password(password)
        if not password_checked:
            return render_template('admin/login.html')

        return redirect(url_for('admin.admin_index'))


"主页"
@admin_blu.route('/index')
@check_user
def admin_index():
    user=g.user
    data={
        'user':user.to_admin_dict()
    }
    return render_template('admin/index.html',data=data)


@admin_blu.route('/user_count')
@check_user
def user_count():
    total_count=User.query.filter(User.is_admin==False).count()
    mon_count=1
    day_count=0
    t = time.localtime()
    begin_mon_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    begin_day_date_str=begin_day_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    mon_count=User.query.filter(User.is_admin==False,User.create_time>begin_mon_date_str).count()
    day_count=User.query.filter(User.is_admin==False,User.create_time>begin_day_date_str).count()
    active_time = []
    active_count = []

    # 取到今天的时间字符串
    today_date_str = ('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday))
    # 转成时间对象
    today_date = datetime.strptime(today_date_str, "%Y-%m-%d")

    for i in range(0, 31):
        # 取到某一天的0点0分
        begin_date = today_date - timedelta(days=i)
        # 取到下一天的0点0分,相当与今天的24点
        end_date = today_date - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    # User.query.filter(User.is_admin == False, User.last_login >= 今天0点0分, User.last_login < 今天24点).count()

    # 反转，让最近的一天显示在最后
    active_time.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }
    return render_template('admin/user_count.html',data=data)



"新闻列表"
@admin_blu.route('/user_list')
@check_user
def user_list():
    user=g.user
    currentPage=request.args.get('page',1)
    totalPage=request.args.get('page',1)
    paginate=User.query.filter(User.is_admin==False).paginate(currentPage,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
    pagenations=paginate.items

    user=[]
    for i in pagenations:
        user.append(i.to_admin_dict())
    data={
        'users':user
    }
    return render_template('admin/user_list.html',data=data)



"新闻审核"
@admin_blu.route('/news_review')
@check_user
def news_review():
    page = request.args.get("p", 1)
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    filters = [News.status != 0]
    # 如果关键字存在，那么就添加关键字搜索
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {"total_page": total_page, "current_page": current_page, "news_list": news_dict_list}

    return render_template('admin/news_review.html', data=context)

@check_user
@admin_blu.route('/news_review_action', methods=["POST"])
def news_review_action():
    """新闻管理中的新闻审核详情（点击 按钮之后的页面）"""
    # 1. 接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2. 参数校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询到指定的新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "accept":
        # 代表接受
        news.status = 0
    else:
        # 代表拒绝
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")



    return jsonify(errno=RET.OK, errmsg="OK")





@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """新闻审核"""
    # 获取新闻id



    """新闻后台新闻审核详情页"""

    # 通过id查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})

    # 返回数据
    data = {"news": news.to_dict()}
    return render_template('admin/news_review_detail.html', data=data)



# "新闻编辑"
@admin_blu.route('/news_edit')
@check_user
def news_edit():
    user=g.user
    try:
        page=request.args.get('p',1)
        keywords=request.args.get('keywords')
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    filters = [News.status == 0]
    if keywords:
        filters.append(News.title.contains(keywords))


    try:
        paginate=News.query.filter(*filters).order_by(News.create_time.desc())\
            .paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询错误')
    pages=paginate.pages
    news_obj_list=paginate.items
    news_list=[]
    for news in news_obj_list:
        news_list.append(news.to_dict())

    data={
        'news_list':news_list,
        'current_page':page,
        'total_page':pages

    }

    return render_template('admin/news_edit.html',data=data)

@admin_blu.route('/news_edit_detail',methods=['POST','GET'])
@check_user
def news_edit_detail():
    if request.method=='GET':
        news_id=request.args.get('news_id')

        try:
            news_id=int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
        try:
            news_obj=News.query.filter(News.id==news_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库查询失败')


        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="查询数据错误")
        category_dict_li = []
        for category in categories:
            # 取到分类的字典
            cate_dict = category.to_dict()
            # 判断当前遍历到的分类是否是当前新闻的分类，如果是，则添加is_selected为true
            if category.id == news_obj.category_id:
                cate_dict["is_selected"] = True
            category_dict_li.append(cate_dict)

        category_dict_li.pop(0)

        data={
            'categories':category_dict_li,
            'news':news_obj.to_dict()
        }

        return render_template('admin/news_edit_detail.html',data=data)
    else:
        digest=request.form.get('digest')
        # index_image=request.form.get('index_image')
        content=request.form.get('content')
        category_id=request.form.get('category_id')
        news_id = request.form.get("news_id")
        title = request.form.get("title")

        if not all([digest,content,category_id,news_id,title]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')


        try:
            news=News.query.get(news_id)
        except Exception as e :
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库查询失败，详情POST')

        if not news:
            return jsonify(errno=RET.DBERR,errmsg='数据库查询失败，详情POST')

        news.title=title
        news.avatar_url=digest
        news.content=content
        news.category_id=category_id
            # news.avatar_url=image(read()后调用，storage生成avatar——url)

        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")
        return jsonify(errno=RET.OK, errmsg='OK')


# "新闻类型"
@admin_blu.route('/news_type')
@check_user
def news_type():
    user=g.user
    categories = Category.query.all()
    # 定义列表保存分类数据
    categories_dicts = []

    for category in categories:
        # 获取字典
        cate_dict = category.to_dict()
        # 拼接内容
        categories_dicts.append(cate_dict)

    categories_dicts.pop(0)
    # 返回内容
    return render_template('admin/news_type.html', data={"categories": categories_dicts})


@admin_blu.route('/add_category', methods=["POST"])
def add_category():
    """修改或者添加分类"""

    category_id = request.json.get("id")
    category_name = request.json.get("name")
    if not category_name:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 判断是否有分类id
    if category_id:
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        if not category:
            return jsonify(errno=RET.NODATA, errmsg="未查询到分类信息")

        category.name = category_name
    else:
        # 如果没有分类id，则是添加分类
        category = Category()
        category.name = category_name
        db.session.add(category)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="保存数据成功")

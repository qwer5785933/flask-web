from crypt import methods

from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request, jsonify
from sqlalchemy.testing import in_

from info import check_user, db
from info import constants
from info.models import News,Comment, CommentLike
from info.utils.response_code import RET
from . import news_blu

@news_blu.route('/<int:news_id>',methods=['POST','GET'])
@check_user
def news_detil(news_id):

    user=g.user
    news_id=news_id

    if not news_id:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    try:
        current_news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询失败')

    news_list=[]
    try:
        news_list_cilck = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')
    for news_click in news_list_cilck:
        news_list.append(news_click.to_dict())
    is_collected=False
    if user:
        try:
            news_collects=user.collection_news
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')
        if current_news in news_collects:
            is_collected=True
    comment_list=[]
    comment = Comment()
    try:
        current_news_comments=current_news.comments
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')

    for comment_ in current_news_comments:
        comment_list.append(comment_.to_dict())
    comment_list_islike = []
    # 点赞
    current_news_comments_list=[comment.id for comment in current_news_comments]
    if user:
        try:

            comment_like=CommentLike.query.filter(CommentLike.user_id==user.id,
                                                      CommentLike.comment_id.in_(current_news_comments_list)).all()
            # print(comment_like)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')

        comments_like_id_list=[comment_l.comment_id for comment_l in comment_like ]


        for i in comment_list:
            if i['id'] in comments_like_id_list:
                i['is_like']=True
                comment_list_islike.append(i)
            else:
                i['is_like'] = False
                comment_list_islike.append(i)

    data={
        'news':current_news.to_dict(),
        'user':g.user if user else None,
        'is_collected':is_collected,
        'comments': comment_list_islike if user else comment_list,
        'news_dict_li':news_list

    }
    return render_template('news/detail.html',data=data)

@news_blu.route('/news_collect',methods=['POST'])
@check_user
def collect():
    user=g.user
    news_id=request.json.get('news_id')
    action=request.json.get('action')
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    if not [news_id,action]:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='数据库查询失败，新闻')



    if not news:
        return jsonify(errno=RET.DBERR,errmsg='参数错误，新闻')
    if user:
        if action=="collect":
            if news not in user.collection_news:
                user.collection_news.append(news)
        else:
            if news in user.collection_news:
                user.collection_news.remove(news)
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(errno=RET.DBERR,errmsg='参数错误，新闻')



    return jsonify(errno=RET.OK,errmsg='OK')


@news_blu.route('/news_comment',methods=['POST'])
@check_user
def new_comment():
    news_id=request.json.get('news_id',None)
    comment=request.json.get('comment',None)
    parent_id=request.json.get('parent_id',None)

    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')




    if not all([news_id,comment]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    try:
        news_id=int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询错误新闻')

    if not news:
        return jsonify(errno=RET.DBERR,errmsg='news数据库查询错误新闻不存在')


    try:
        comment_mod=Comment()
        comment_mod.content=comment
        comment_mod.user_id=user.id if user else None
        comment_mod.news_id=news_id
        if parent_id:
            comment_mod.parent_id = parent_id
    except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='newscomment数据库添加错误')
    try:
        db.session.add(comment_mod)
        db.session.commit()
    except Exception as e :
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库提交错误')

    data=comment_mod.to_dict()
    return jsonify(errno=RET.OK, errmsg='OK',data=data)



@news_blu.route('/comment_like',methods=['POST'])
@check_user
def comment_like():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    comment_id=request.json.get('comment_id')
    # news_id=request.json.get('news_id')
    action=request.json.get('action') #add remove str

    try:
        comment_id=int(comment_id)
        # news_id=int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="用户参数类型错误")

    if not all([comment_id,comment_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="用户参数错误")

    if action not in ['add','remove']:
        return jsonify(errno=RET.PARAMERR, errmsg="用户参数错误")

    comment=Comment.query.get(comment_id)
    if action == 'add':
        comment_like_model= CommentLike.query.filter(CommentLike.user_id == user.id,
                                                     CommentLike.comment_id == comment.id).first()
        if not comment_like_model:
            comment_like_model=CommentLike()
            comment_like_model.user_id=user.id
            comment_like_model.comment_id=comment.id
            comment.like_count += 1
            try:
                db.session.add(comment_like_model)
                db.session.add(comment)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR,errmsg='数据库写入')
        else:
            return jsonify(errno=RET.DBERR, errmsg='数据库误删除，或者前端代码逻辑 错误1')

    else:
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()
        if comment_like_model:
            try:
                db.session.delete(comment_like_model)
                comment.like_count -= 1
                db.session.add(comment)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR,errmsg='数据库删除失败')

        else:
            return jsonify(errno=RET.DBERR, errmsg='数据库误删除，或者前端代码逻辑 错误2')
    return jsonify(errno=RET.OK, errmsg="操作成功")

    # cur_news=News.query.get(news_id)
    # comment_like=CommentLike.query.filter(user.id==CommentLike.user_id)
    # comment_like_list=Comment.query.filter(comment_like.comment_id in_ cur_news.comments.id)
    # cur_news=News.query.get(news_id)














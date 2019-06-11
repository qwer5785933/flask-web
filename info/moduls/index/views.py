from flask import current_app
from flask import render_template

from info import redis_store
from . import index_

@index_.route('/')
def hello_world():
    redis_store.set('name','laowang')
    print(redis_store.get('name').decode())


    return render_template('news/index.html')

@index_.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
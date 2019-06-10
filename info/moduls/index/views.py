from flask import render_template

from info import redis_store
from . import index_

@index_.route('/')
def hello_world():
    redis_store.set('name','laowang')
    print(redis_store.get('name').decode())
    print(1)

    return render_template('news/index.html')
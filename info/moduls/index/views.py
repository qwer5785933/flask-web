

from . import index_

@index_.route('/')
def hello_world():

    return 'Hello World!'
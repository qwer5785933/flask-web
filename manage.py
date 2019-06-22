from info import db, create_app,models
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from config import *
from info.models import User

app=create_app('development')

"""
:parameter
development':DevelopmentConfig,
'production':ProductionConfig,
'testing':TestingConfig
"""

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.option('-n', '--name', dest='name')
@manager.option('-p', '--password', dest='password')
def createsuperuser(name,password):
    if not all([name,password]):
        print('参数不足')
        return
    user=User()
    user.nick_name=name
    user.mobile=name
    user.is_admin=True
    user.name=name
    user.password=password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    print('创建成功')


if __name__ == '__main__':

    manager.run()

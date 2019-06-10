from info import db, create_app,models
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from config import *



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





if __name__ == '__main__':
    manager.run()

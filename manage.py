from info import app ,db, create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from config import *




app_selected_config=create_app('development')
"""
:parameter
development':DevelopmentConfig,
'production':ProductionConfig,
'testing':TestingConfig
"""

manager = Manager(app_selected_config)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()

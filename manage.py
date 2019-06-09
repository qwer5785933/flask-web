from info import app ,db
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand






manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()

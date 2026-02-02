from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from modules.todo import Todo
from modules.db_instance import db
from api.task import task_bp
from api.time import time_bp
import os

def create_app():
    app = Flask(__name__)
    USE_POSTGRESQL = os.environ.get('USE_POSTGRESQL') == '1'

    if USE_POSTGRESQL:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://todo_user:todo_password@localhost/todo_db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(task_bp, url_prefix='/api/task')
    app.register_blueprint(time_bp, url_prefix='/api/time')

    @app.route("/", methods=["GET", "POST"])
    def home():
        todo_list = Todo.query.all()

        # データベース情報を取得
        db_info = None
        if USE_POSTGRESQL:
            db_info = {
                'type': 'PostgreSQL',
                'modules': 'todo_db',
                'user': 'todo_user',
                'host': 'localhost'
            }
        return render_template("index.html", todo_list=todo_list, db_info=db_info)
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Blueprint,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

bp = Blueprint('task', __name__)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

@bp.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@bp.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))
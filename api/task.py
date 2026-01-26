from flask import Blueprint,request, redirect, url_for
from modules.todo import db, Todo

bp = Blueprint('task', __name__)

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

@bp.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return "Todo not found", 404
    title = request.form.get("title")
    todo.title = title
    db.session.commit()
    return redirect(url_for("home"))
from datetime import datetime
from flask import Blueprint,request, redirect, url_for
from modules.todo import db, Todo

time_bp = Blueprint('time', __name__)

@time_bp.route("/<int:todo_id>/start", methods=["POST"])
def start(todo_id):
    todo_id = Todo.query.get(todo_id)
    todo = Todo.query.get(todo_id)
    if todo is None:
        return "Todo not found", 404
    todo.started_by_time = datetime.now()
    db.session.commit()
    return redirect(url_for("timer"))

@time_bp.route("/<int:todo_id>/end", methods=["POST"])
def end(todo_id):
    todo = Todo.query.get(todo_id)
    now = datetime.now()
    if todo is None:
        return "Todo not found", 404
    if todo.started_by_time:
        todo.ended_by_time = now
        duration = (now - todo.started_by_time).total_seconds()
        todo.duration_seconds = int(duration)
        db.session.commit()
    else:
        return "Task has not been started", 400
    return redirect(url_for("timer"))
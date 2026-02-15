from datetime import datetime
from flask import Blueprint,request, redirect, url_for
from app.models.task import db, Task

time_bp = Blueprint('time', __name__)

@time_bp.route("/<int:todo_id>/start", methods=["POST"])
def start(todo_id):
    todo_id = (Task.query.get(todo_id))
    todo = Task.query.get(todo_id)
    if todo is None:
        return "Todo not found", 404
    todo.started_date = datetime.now().date()
    todo.started_by_time = datetime.now()
    db.session.commit()
    return redirect(url_for("timer"))

@time_bp.route("/<int:todo_id>/end", methods=["POST"])
def end(todo_id):
    todo = Task.query.get(todo_id)
    now_time = datetime.now()
    now_date = now_time.date()
    if todo is None:
        return "Todo not found", 404
    if todo.started_by_time:
        todo.ended_by_time = now_time
        duration = (now_time - todo.started_by_time).total_seconds()
        todo.duration_seconds = int(duration)
        todo.ended_date = now_date
        db.session.commit()
    else:
        return "Task has not been started", 400
    return redirect(url_for("timer"))
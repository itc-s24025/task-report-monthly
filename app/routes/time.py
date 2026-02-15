from datetime import datetime
from flask import Blueprint, request, redirect, url_for, jsonify, session
from app.models.task import db, Task

time_bp = Blueprint('time', __name__)

@time_bp.route("/<int:todo_id>/start", methods=["POST"])
def start(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    todo.started_time = datetime.now()
    todo.started_date = datetime.now().date()
    db.session.commit()
    return jsonify({"status": "started", "start_time": todo.started_time.isoformat()})

@time_bp.route("/<int:todo_id>/end", methods=["POST"])
def end(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    now_time = datetime.now()
    now_date = now_time.date()
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    if todo.started_time:
        todo.ended_time = now_time
        duration = (now_time - todo.started_time).total_seconds()
        todo.duration_seconds = int(duration)
        todo.ended_date = now_date
        db.session.commit()
        return jsonify({
            "status": "stopped",
            "end_time": todo.ended_time.isoformat(),
            "duration_seconds": todo.duration_seconds
        })
    else:
        return jsonify({"error": "Task has not been started"}), 400

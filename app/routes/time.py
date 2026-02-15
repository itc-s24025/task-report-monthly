from datetime import datetime
from flask import Blueprint, request, redirect, url_for, jsonify
from app.models.task import db, Task

time_bp = Blueprint('time', __name__)

@time_bp.route("/<int:todo_id>/start", methods=["POST"])
def start(todo_id):
    todo = Task.query.get(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    
    todo.started_time = datetime.now()
    db.session.commit()
    return jsonify({"status": "started", "start_time": todo.started_time.isoformat()})

@time_bp.route("/<int:todo_id>/end", methods=["POST"])
def end(todo_id):
    todo = Task.query.get(todo_id)
    now = datetime.now()
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    
    if todo.started_time:
        todo.ended_time = now
        duration = (now - todo.started_time).total_seconds()
        todo.duration_seconds = int(duration)
        db.session.commit()
        return jsonify({
            "status": "stopped", 
            "end_time": todo.ended_time.isoformat(),
            "duration_seconds": todo.duration_seconds
        })
    else:
        return jsonify({"error": "Task has not been started"}), 400

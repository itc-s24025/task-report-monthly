from flask import Blueprint, request, jsonify, session, redirect, url_for
from datetime import datetime
from app import db
from app.models.task import Task

task_bp = Blueprint("task", __name__, url_prefix="/api/tasks")


def _parse_datetime(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.fromisoformat(s + 'T00:00:00')
        except Exception:
            return None


@task_bp.route("", methods=["POST"])
def create_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()

    task = Task()
    task.user_id = user_id
    task.task_name = data["task_name"]
    task.start_time = data["start_time"]
    task.end_time = data["end_time"]
    task.category_id = data["category_id"]
    task.memo = data.get("memo", "")
    task = Task(
        user_id=user_id,
        task_name=data.get("task_name","(無題)"),
        category_id=data.get("category_id"),
        memo=data.get("memo"),
    )

    # optional: created_date (keep backward compatibility)
    if data.get("created_date"):
        try:
            task.created_date = datetime.strptime(data["created_date"], "%Y-%m-%d").date()
        except Exception:
            pass

    # calendar fields
    start = _parse_datetime(data.get("start") or data.get("start_time"))
    end = _parse_datetime(data.get("end") or data.get("end_time"))
    if start:
        task.start_time = start
    if end:
        task.end_time = end

    db.session.add(task)
    db.session.commit()

    return jsonify({"status": "created", "task_id": task.id})


@task_bp.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@task_bp.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return "Todo not found", 404
    title = request.form.get("title")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    category_id = request.form.get("category_id")
    memo = request.form.get("memo")
    todo.title = title
    todo.start_time = start_time
    todo.end_time = end_time
    todo.category_id = category_id
    todo.memo = memo
    db.session.commit()
    return redirect(url_for("home"))
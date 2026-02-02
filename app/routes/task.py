from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app import db
from app.models.task import Task

task_bp = Blueprint("task", __name__, url_prefix="/api/tasks")

@task_bp.route("", methods=["POST"])
def create_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()

    task = Task(
        user_id=user_id,
        task_name=data["task_name"],
        category_id=data["category_id"],
        memo=data.get("memo"),
        created_date=datetime.strptime(
            data["created_date"], "%Y-%m-%d"
        ).date()
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"status": "created", "task_id": task.id})

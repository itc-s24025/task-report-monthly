from flask import Blueprint, request, jsonify, session
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


@task_bp.route("", methods=["GET"])
def list_tasks():
    """Return tasks in a given date range for FullCalendar.
    Expects ?start=YYYY-MM-DD&end=YYYY-MM-DD (end is exclusive)
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([]), 401

    start_str = request.args.get("start")
    end_str = request.args.get("end")
    start_dt = _parse_datetime(start_str)
    end_dt = _parse_datetime(end_str)

    q = db.select(Task).where(Task.user_id == user_id)
    if start_dt and end_dt:
        q = q.where(Task.start_time >= start_dt, Task.start_time < end_dt)

    tasks = db.session.execute(q).scalars().all()

    events = []
    for t in tasks:
        events.append({
            "id": t.id,
            "title": t.task_name,
            "start": t.start_time.isoformat() if t.start_time else None,
            "end": t.end_time.isoformat() if t.end_time else None,
            "extendedProps": {
                "memo": t.memo,
                "category_id": t.category_id,
            },
        })

    return jsonify(events)


@task_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    task = db.session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return jsonify({"error": "not found"}), 404

    if "task_name" in data:
        task.task_name = data["task_name"]
    if "memo" in data:
        task.memo = data.get("memo")
    if "category_id" in data:
        task.category_id = data.get("category_id")

    start = _parse_datetime(data.get("start") or data.get("start_time"))
    end = _parse_datetime(data.get("end") or data.get("end_time"))
    if start is not None:
        task.start_time = start
    if end is not None:
        task.end_time = end

    db.session.commit()
    return jsonify({"status": "ok"})


@task_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    task = db.session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return jsonify({"error": "not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"status": "deleted"})

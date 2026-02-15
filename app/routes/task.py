from flask import Blueprint, request, jsonify, session, current_app
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


@task_bp.route("", methods=["POST", "GET"])
def create_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    if request.method == "GET":
        # データベースからログインユーザーのタスクを取得
        tasks = Task.query.filter_by(user_id=user_id).all()

        # 以前は GET でも body(JSON) で start/end を受け取っていたが
        # クライアントからは query パラメータで渡すのが一般的なので両方対応する
        data = request.get_json(silent=True) or {}
        # request.args を優先して使う
        start = request.args.get('start') or data.get("start")
        end = request.args.get('end') or data.get("end")
        if start and end:
            start_dt = _parse_datetime(start)
            end_dt = _parse_datetime(end)
            tasks = Task.query.filter(
                Task.user_id == user_id,
                Task.start_time >= start_dt,
                Task.end_time <= end_dt
            ).all()

            return jsonify([{
                'status': 'success',
                'id': t.id,
                'task_name': t.task_name,
                'start_time': t.start_time.isoformat() if t.start_time else None,
                'end_time': t.end_time.isoformat() if t.end_time else None,
                'category_id': t.category_id,
                'extendedProps': {'memo': t.memo}
            } for t in tasks])

        # FullCalendarが理解できる形式に変換
        return jsonify([{
            'status': 'success',
            'id': t.id,
            'task_name': t.task_name,
            'start_time': t.start_time.isoformat() if t.start_time else None,
            'end_time': t.end_time.isoformat() if t.end_time else None,
            'extendedProps': {'memo': t.memo}
        } for t in tasks])

    elif request.method == "POST":
        data = request.get_json()

        task = Task()
        task.user_id = user_id
        task.task_name = data["task_name"]
        task.start_time = data["start_time"]
        task.end_time = data["end_time"]
        task.category_id = data.get("category_id")
        task.memo = data.get("memo", "")

        db.session.add(task)
        db.session.commit()

        return jsonify({"status": "created", "task_id": task.id})


@task_bp.route("/<int:todo_id>", methods=["DELETE"])
def delete(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"status": "deleted"})


@task_bp.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    todo = Task.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return jsonify({"error": "not_found"}), 404
    title = request.form.get("task_name")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    category_id = request.form.get("category_id")
    memo = request.form.get("memo")
    # apply updates with parsing
    if title is not None:
        todo.task_name = title
    if start_time is not None:
        parsed_start = _parse_datetime(start_time)
        if parsed_start:
            todo.start_time = parsed_start
            todo.started_date = parsed_start.date()
    if end_time is not None:
        parsed_end = _parse_datetime(end_time)
        if parsed_end:
            todo.end_time = parsed_end
            todo.ended_date = parsed_end.date()
    if category_id is not None:
        try:
            todo.category_id = int(category_id)
        except Exception:
            todo.category_id = None
    if memo is not None:
        todo.memo = memo

    # recompute duration_seconds if both datetimes present
    try:
        if todo.start_time and todo.end_time:
            delta = todo.end_time - todo.start_time
            seconds = int(delta.total_seconds()) if delta.total_seconds() > 0 else 0
            todo.duration_seconds = seconds
    except Exception:
        pass
    db.session.commit()
    # Return JSON for API clients
    return jsonify({"status": "updated"})


@task_bp.route('/debug', methods=['GET'])
def debug_tasks():
    """開発時のみ有効なデバッグエンドポイント。
    app.debug が True のときのみ動作し、全ユーザーのタスクまたは user_id クエリで指定したユーザーのタスクを返す。
    本番環境ではセキュリティ上無効化してください。
    """
    if not current_app.debug:
        return jsonify({"error": "disabled"}), 403

    uid = request.args.get('user_id')
    if uid:
        tasks = Task.query.filter_by(user_id=uid).all()
    else:
        tasks = Task.query.limit(200).all()

    return jsonify([{
        'id': t.id,
        'task_name': t.task_name,
        'start_time': t.start_time.isoformat() if t.start_time else None,
        'end_time': t.end_time.isoformat() if t.end_time else None,
        'memo': t.memo,
        'category_id': t.category_id
    } for t in tasks])

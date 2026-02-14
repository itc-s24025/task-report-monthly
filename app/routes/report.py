from flask import Blueprint, request, redirect, url_for, jsonify
from sqlalchemy import func, extract
from app.models.task import Task
from app.models.category import Category
from app import db

report_bp = Blueprint('filter', __name__, url_prefix="/api/report")

@report_bp.route("/project", methods=["GET"])
def project():
    # 全体の合計時間を計算
    total_duration = db.session.query(
        func.sum(Task.duration_seconds)
    ).scalar() or 0

    # タスク名と日付ごとに集計
    todo_list = (
        db.session.query(
            Task.task_name,
            func.coalesce(Task.started_date, Task.created_date).label('work_date'),
            func.sum(Task.duration_seconds).label('total_duration')
        )
        .group_by(Task.task_name, func.coalesce(Task.started_date, Task.created_date))
        .order_by(func.sum(Task.duration_seconds).desc())
        .all()
    )

    return jsonify({
        "data": [
            {
                "task_name": todo.task_name,
                "work_date": todo.work_date.isoformat() if todo.work_date else "",
                "total_hour": round((todo.total_duration or 0) / 3600, 1),
                "progress": round(((todo.total_duration or 0) / total_duration) * 100, 1) if total_duration else 0
            }
            for todo in todo_list
        ]
    })

@report_bp.route("/category", methods=["GET"])
def category():
    # カテゴリ別に集計（Categoryテーブルと結合）
    todo_list = (
        db.session.query(
            Category.category_name,
            func.sum(Task.duration_seconds).label('total_duration'),
            func.sum(Task.end_time - Task.start_time).label('planned_duration')
        )
        .outerjoin(Category, Task.category_id == Category.id)
        .group_by(Task.category_id, Category.category_name)
        .order_by(func.sum(Task.duration_seconds).desc())
        .all()
    )

    return jsonify({
        "data": [
            {
                "category_name": todo.category_name if todo.category_name else "未分類",
                "total_hour": round((todo.total_duration or 0) / 3600, 1),
                "progress": round((todo.planned_duration.total_seconds() / todo.total_duration) * 100, 1) if todo.planned_duration and todo.total_duration else 0
            }
            for todo in todo_list
        ]
    })

@report_bp.route("/monthly", methods=["GET"])
def monthly():
    # GETパラメータから取得
    year = request.args.get("year")
    month = request.args.get("month")

    # 月次集計
    month_todo = db.session.query(
        func.sum(Task.duration_seconds).label('total_duration'),
        func.count(Task.id).label('total_day')
    ).filter(
        extract('year', Task.started_date) == year,
        extract('month', Task.started_date) == month,
    ).first()

    return jsonify({
        "total_hour": round((month_todo.total_duration or 0) / 3600, 1) if month_todo else 0,
        "total_day": month_todo.total_day if month_todo else 0
    })
from babel.messages.extract import extract
from flask import Blueprint,request, redirect, url_for, jsonify
from sqlalchemy import func
from app.models.task import Task
from app import db

report_bp = Blueprint('filter', __name__, url_prefix="/api/report")

@report_bp.route("project", methods=["GET"])
def category():
    todo_list = (db.session.query(
        func.sum(Task.duration_seconds).label('total_duration'),
        func.sum(Task.end_time - Task.start_time).label('planned_duration')
    ).group_by(
        Task.id
    ).order_by(func.sum(Task.duration_seconds).desc()).all())

    return jsonify({
        "data": [
            {
                "project_name": todo.task_name if todo.task_name else "名前がありません",
                "total_hour": round(todo.total_duration / 3600, 1),
                "progress": round(
                    round(todo.planned_duration.total_seconds() / 3600, 1) / round(todo.total_duration / 3600,1)) * 100 if todo.planned_duration else 0
            }
            for todo in todo_list
        ]
    })

@report_bp.route("category", methods=["GET"])
def category():
    todo_list = (db.session.query(
        func.sum(Task.duration_seconds).label('total_duration'),
        func.sum(Task.end_time - Task.start_time).label('planned_duration')
    ).group_by(
        Task.category_id
    ).order_by(func.sum(Task.duration_seconds).desc()).all())

    return jsonify({
        "data": [
            {
                "category_name": todo.category.category_name if todo.category else "未分類",
                "total_hour": round(todo.total_duration / 3600 , 1),
                "progress": round(round(todo.planned_duration.total_seconds() / 3600 , 1) / round(todo.total_duration / 3600 , 1)) * 100 if todo.planned_duration else 0
            }
            for todo in todo_list
        ]
    })

@report_bp.route("monthly", methods=["GET"])
def monthly():
    data = request.get_json()
    year = data["year"]
    month = data["month"]
    month_todo = db.session.query(
        extract('year', Task.started_date).label('year'),
        extract('month', Task.started_date).label('month'),
        func.sum(Task.duration_seconds).label('total_duration'),
        func.count(Task.id).label('total_day')
    ).filter(
        extract('year', Task.started_date) == year,
        extract('month', Task.started_date) == month,
    ).group_by(
        extract('year', Task.started_date),
        extract('month', Task.started_date)
    ).first
    # month_todo の中身（イメージ）
    # (2026, 2, 3600.0)

    return jsonify({
        "total_hour": round(month_todo.total_duration / 3600 , 1) if month_todo else 0,
        "total_day": month_todo.total_day if month_todo else 0
    })
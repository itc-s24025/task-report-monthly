from flask import Blueprint, request, redirect, url_for, jsonify
from sqlalchemy import func, extract
from app.models.task import Task
from app.models.category import Category
from app import db

report_bp = Blueprint('filter', __name__, url_prefix="/api/report")


def _parse_year_month():
    year = request.args.get("year")
    month = request.args.get("month")

    try:
        year = int(year) if year else None
    except (TypeError, ValueError):
        year = None

    try:
        month = int(month) if month else None
    except (TypeError, ValueError):
        month = None

    if month is not None and (month < 1 or month > 12):
        month = None

    return year, month


def _apply_year_month_filter(query, date_column, year, month):
    if year is not None:
        query = query.filter(extract('year', date_column) == year)
    if month is not None:
        query = query.filter(extract('month', date_column) == month)
    return query


@report_bp.route("/project", methods=["GET"])
def project():
    year, month = _parse_year_month()
    # 実行予定日（start_time）から日付を抽出、なければ登録日を使用
    schedule_date = func.coalesce(
        func.date(Task.start_time),
        Task.created_date
    )

    # 全体の合計時間を計算
    total_query = db.session.query(
        func.sum(Task.duration_seconds)
    )
    total_query = _apply_year_month_filter(total_query, schedule_date, year, month)
    total_duration = total_query.scalar() or 0

    # タスク名、予定日、終了日ごとに集計
    todo_query = (
        db.session.query(
            Task.task_name,
            schedule_date.label('work_date'),
            Task.ended_date,
            func.sum(Task.duration_seconds).label('total_duration')
        )
    )
    todo_query = _apply_year_month_filter(todo_query, schedule_date, year, month)
    todo_list = (
        todo_query
        .group_by(Task.task_name, schedule_date, Task.ended_date)
        .order_by(func.sum(Task.duration_seconds).desc())
        .all()
    )

    return jsonify({
        "data": [
            {
                "task_name": todo.task_name,
                "work_date": todo.work_date.isoformat() if todo.work_date else "",
                "ended_date": todo.ended_date.isoformat() if todo.ended_date else "",
                "total_hour": round((todo.total_duration or 0) / 3600, 1),
                "progress": round(((todo.total_duration or 0) / total_duration) * 100, 1) if total_duration else 0
            }
            for todo in todo_list
        ]
    })


@report_bp.route("/category", methods=["GET"])
def category():
    year, month = _parse_year_month()
    date_column = func.coalesce(Task.started_date, Task.created_date)

    # カテゴリ別に集計（Categoryテーブルと結合）
    todo_query = (
        db.session.query(
            Category.category_name,
            func.sum(Task.duration_seconds).label('total_duration'),
            func.sum(Task.end_time - Task.start_time).label('planned_duration')
        )
        .outerjoin(Category, Task.category_id == Category.id)
    )
    todo_query = _apply_year_month_filter(todo_query, date_column, year, month)
    todo_list = (
        todo_query
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
    year, month = _parse_year_month()
    date_column = func.coalesce(Task.started_date, Task.created_date)

    # 月次集計
    month_query = db.session.query(
        func.sum(Task.duration_seconds).label('total_duration'),
        func.count(Task.id).label('total_day')
    )
    month_query = _apply_year_month_filter(month_query, date_column, year, month)
    month_todo = month_query.first()

    return jsonify({
        "total_hour": round((month_todo.total_duration or 0) / 3600, 1) if month_todo else 0,
        "total_day": month_todo.total_day if month_todo else 0
    })
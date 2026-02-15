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

    # 1. フィルタリング用の基準（今月のデータを抽出するため）
    filter_target = Task.started_date

    # 2. 総作業時間（秒）を算出
    total_duration_q = (
        db.session.query(func.sum(Task.duration_seconds).label('total_duration'))
        .select_from(Task)
    )
    total_duration_q = _apply_year_month_filter(total_duration_q, filter_target, year, month)
    total_duration_row = total_duration_q.first()
    total_seconds = total_duration_row.total_duration if total_duration_row and total_duration_row.total_duration else 0

    # 3. 総作業日数（日をまたぐ期間の合計）を算出
    # 各タスクの (終了日 - 開始日 + 1) を合計する
    # func.coalesce は NULL だった場合に 0 や 1 を扱うための安全策
    total_day_q = (
        db.session.query(
            func.sum(
                Task.ended_date - Task.started_date + 1
            ).label('total_day')
        )
        .select_from(Task)
    )
    # ここでも「今月のタスク」に絞り込むために filter_target を使用
    total_day_q = _apply_year_month_filter(total_day_q, filter_target, year, month)

    total_day_row = total_day_q.first()
    total_day = total_day_row.total_day if total_day_row and total_day_row.total_day else 0

    return jsonify({
        "total_hour": round(total_seconds / 3600, 1) if total_seconds else 0,
        "total_day": int(total_day)
    })
from flask import Blueprint, request, redirect, url_for, jsonify
from sqlalchemy import func, extract, case, text
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
    # 期間フィルタに使う日付：start_time の日付部分のみを使う
    schedule_date = func.date(Task.start_time)

    # 作業時間は started_time/ended_time が両方ある場合にのみ (ended_time - started_time) を計算する
    # それ以外は NULL として扱う（表示しない要件に対応）
    duration_expr = case(
        ( (Task.started_time.isnot(None)) & (Task.ended_time.isnot(None)), func.extract('epoch', (Task.ended_time - Task.started_time)) ),
        else_=None
    )

    # 全体の合計時間（秒）を計算（ended_date が無いレコードは除外）
    total_query = db.session.query(func.sum(duration_expr)).select_from(Task).filter(Task.ended_date.isnot(None))
    total_query = _apply_year_month_filter(total_query, schedule_date, year, month)
    total_duration = total_query.scalar() or 0

    # タスク名、予定日、終了日ごとに集計（秒）
    todo_query = (
        db.session.query(
            Task.task_name,
            schedule_date.label('work_date'),
            Task.ended_date,
            func.sum(duration_expr).label('total_duration')
        )
    )
    todo_query = _apply_year_month_filter(todo_query, schedule_date, year, month)
    todo_list = (
        todo_query
        .group_by(Task.task_name, schedule_date, Task.ended_date)
        .order_by(func.sum(duration_expr).desc())
        .all()
    )

    return jsonify({
        "data": [
            {
                "task_name": todo.task_name,
                "work_date": todo.work_date.isoformat() if getattr(todo, 'work_date', None) else "",
                "ended_date": todo.ended_date.isoformat() if todo.ended_date else "",
                # total_duration が None の場合（該当グループに開始/終了時刻の揃ったレコードがない）
                # 表示しないため null を返す
                "total_hour": float(round(todo.total_duration / 3600, 1)) if todo.total_duration is not None else None,
                "progress": float(round(((todo.total_duration) / total_duration) * 100, 1)) if (todo.total_duration is not None and total_duration) else None
            }
            for todo in todo_list
        ]
    })


@report_bp.route("/category", methods=["GET"])
def category():
    year, month = _parse_year_month()
    # 日付フィルタは start_time の日付部分を使う（created_date ではなく start_time に統一）
    date_column = func.date(Task.start_time)

    # duration を started/ended で計算（秒）を優先し、ただし started/ended が両方存在しない場合は NULL
    duration_expr = case(
        ( (Task.started_time.isnot(None)) & (Task.ended_time.isnot(None)), func.extract('epoch', (Task.ended_time - Task.started_time)) ),
        else_=None
    )

    # 全体合計（ended_date が存在するレコードのみ）
    total_all_q = db.session.query(func.sum(duration_expr)).select_from(Task).filter(Task.ended_date.isnot(None))
    total_all_q = _apply_year_month_filter(total_all_q, date_column, year, month)
    total_all = total_all_q.scalar() or 0

    # カテゴリ別の合計を取得（Task を起点に明示的に select_from）
    todo_query = (
        db.session.query(
            Category.id.label('category_id'),
            Category.category_name,
            func.sum(duration_expr).label('total_duration')
        )
        .select_from(Task)
        .outerjoin(Category, Task.category_id == Category.id)
    )
    # 表示は ended_date が無くても含める（終了日セルは空にする）
    todo_query = _apply_year_month_filter(todo_query, date_column, year, month)
    todo_list = (
        todo_query
        .group_by(Category.id, Category.category_name)
        .order_by(func.sum(duration_expr).desc())
        .all()
    )

    return jsonify({
        "data": [
            {
                "category_id": todo.category_id,
                "category_name": todo.category_name if todo.category_name else "未分類",
                "total_hour": float(round((todo.total_duration) / 3600, 1)) if todo.total_duration is not None else None,
                "progress": float(round(((todo.total_duration) / total_all) * 100, 1)) if (todo.total_duration is not None and total_all) else None
            }
            for todo in todo_list
        ]
    })


@report_bp.route("/monthly", methods=["GET"])
def monthly():
    # GETパラメータから取得
    year, month = _parse_year_month()

    # 1. フィルタリング用の基準（started_date の date カラムを基準にする）
    filter_target = Task.started_date

    # 総作業時間（秒）を算出（ended_date があるもののみ）
    total_duration_q = (
        db.session.query(func.sum(Task.duration_seconds).label('total_duration')).select_from(Task).filter(Task.ended_date.isnot(None))
    )
    total_duration_q = _apply_year_month_filter(total_duration_q, filter_target, year, month)
    total_duration_row = total_duration_q.first()
    total_seconds = total_duration_row.total_duration if total_duration_row and total_duration_row.total_duration else 0

    # 3. 総作業日数: タスクの開始日〜終了日を日単位で展開し、対象月内のユニークな日数をカウントする
    # 使用する DB 関数は Postgres の generate_series(date, date, interval '1 day')
    # 1) 対象月の start_date / end_date を決定
    from datetime import date as _date
    import calendar as _calendar
    if year is None or month is None:
        today = _date.today()
        start_date = _date(today.year, today.month, 1)
        end_date = _date(today.year, today.month, _calendar.monthrange(today.year, today.month)[1])
    else:
        start_date = _date(year, month, 1)
        end_date = _date(year, month, _calendar.monthrange(year, month)[1])

    # 2) Raw SQL: 対象月と重なる started_date/ended_date を持つタスクの各日を展開し、ユニークカウント
    sql = text(
        """
        SELECT count(DISTINCT d)::int AS total_day FROM (
          SELECT generate_series(GREATEST(started_date, CAST(:start_date AS DATE)), LEAST(ended_date, CAST(:end_date AS DATE)), '1 day')::date AS d
          FROM tasks
          WHERE started_date IS NOT NULL
            AND ended_date IS NOT NULL
            AND started_date <= CAST(:end_date AS DATE)
            AND ended_date >= CAST(:start_date AS DATE)
        ) s
        """
    )
    res = db.session.execute(sql, {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}).first()
    total_day = int(res.total_day) if res and res.total_day is not None else 0

    return jsonify({
        "total_hour": round(total_seconds / 3600, 1) if total_seconds else 0,
        "total_day": int(total_day)
    })
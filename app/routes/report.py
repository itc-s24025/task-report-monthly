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

    # 各プロジェクト（task_name）ごとの合計時間も取得して、行ごとの進捗をプロジェクト内比率で計算する
    # 実働（actual）での合計（これを表示の total_hour に使う）
    task_total_q = (
        db.session.query(Task.task_name, func.sum(duration_expr).label('task_total')).select_from(Task).filter(Task.ended_date.isnot(None))
    )
    task_total_q = _apply_year_month_filter(task_total_q, schedule_date, year, month)
    task_total_q = task_total_q.group_by(Task.task_name)
    task_totals = {row.task_name: (row.task_total or 0) for row in task_total_q.all()}

    # 予定時間（planned）: start_time と end_time の差を秒で算出し、プロジェクトごとの予定合計を取得
    planned_expr = case(
        ((Task.start_time.isnot(None)) & (Task.end_time.isnot(None)), func.extract('epoch', (Task.end_time - Task.start_time))),
        else_=None
    )
    planned_q = (
        db.session.query(Task.task_name, func.sum(planned_expr).label('planned_total')).select_from(Task)
    )
    planned_q = _apply_year_month_filter(planned_q, schedule_date, year, month)
    planned_q = planned_q.group_by(Task.task_name)
    planned_totals = {row.task_name: (row.planned_total or 0) for row in planned_q.all()}

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
                "progress": (
                    float(round((todo.total_duration / planned_totals.get(todo.task_name)) * 100, 1))
                    if (todo.total_duration is not None and planned_totals.get(todo.task_name)) else None
                )
            }
            for todo in todo_list
         ]
    })


@report_bp.route("/category", methods=["GET"])
def category():
    year, month = _parse_year_month()
    # 日付フィルタは start_time の日付部分を使う（created_date ではなく start_time に統一）
    date_column = func.date(Task.start_time)

    # 実働 (actual) を started_time/ended_time の差で計算（秒）
    duration_expr = case(
        ( (Task.started_time.isnot(None)) & (Task.ended_time.isnot(None)), func.extract('epoch', (Task.ended_time - Task.started_time)) ),
        else_=None
    )

    # 予定 (planned) を start_time/end_time の差で計算（秒）
    planned_expr = case(
        ( (Task.start_time.isnot(None)) & (Task.end_time.isnot(None)), func.extract('epoch', (Task.end_time - Task.start_time)) ),
        else_=None
    )

    # 1) カテゴリ × タスクごとの実働合計を取得（ended_date があるもののみを集計）
    actual_q = (
        db.session.query(Task.category_id, Task.task_name, func.sum(duration_expr).label('actual'))
        .select_from(Task)
        .filter(Task.ended_date.isnot(None))
    )
    actual_q = _apply_year_month_filter(actual_q, date_column, year, month)
    actual_q = actual_q.group_by(Task.category_id, Task.task_name)
    actual_rows = actual_q.all()

    # 2) カテゴリ × タスクごとの予定合計を取得
    planned_q = (
        db.session.query(Task.category_id, Task.task_name, func.sum(planned_expr).label('planned'))
        .select_from(Task)
    )
    planned_q = _apply_year_month_filter(planned_q, date_column, year, month)
    planned_q = planned_q.group_by(Task.category_id, Task.task_name)
    planned_rows = planned_q.all()

    # 3) カテゴリ合計（実働）を計算
    category_actual = {}
    task_actual_map = {}
    for r in actual_rows:
        category_actual[r.category_id] = category_actual.get(r.category_id, 0) + (r.actual or 0)
        task_actual_map[(r.category_id, r.task_name)] = r.actual

    planned_map = { (r.category_id, r.task_name): r.planned for r in planned_rows }

    # 4) カテゴリ一覧を取得し、カテゴリごとのタスク一覧を組み立てる
    categories = db.session.query(Category).order_by(Category.id).all()
    data = []
    for c in categories:
        cat_total = category_actual.get(c.id, 0)
        # collect task names that have either actual or planned in this category
        names = set()
        for (cat_id, tname) in list(task_actual_map.keys()) + list(planned_map.keys()):
            if cat_id == c.id:
                names.add(tname)
        tasks = []
        for name in sorted(names):
            actual = task_actual_map.get((c.id, name))
            planned = planned_map.get((c.id, name))
            tasks.append({
                'task_name': name,
                'total_hour': float(round(actual / 3600, 1)) if actual is not None else None,
                'progress': float(round((actual / planned) * 100, 1)) if (actual is not None and planned and planned > 0) else None
            })

        data.append({
            'category_id': c.id,
            'category_name': c.category_name or '未分類',
            'total_hour': float(round(cat_total / 3600, 1)) if cat_total else None,
            'tasks': tasks
        })

    return jsonify({'data': data})


@report_bp.route("/monthly", methods=["GET"])
def monthly():
    # GETパラメータから取得
    year, month = _parse_year_month()

    # 1. フィルタリング用の基準（start_time の日付部分を基準とする）
    date_column = func.date(Task.start_time)

    # duration を started_time/ended_time の差（秒）で計算（両方あるもののみを対象）
    duration_expr = case(
        ( (Task.started_time.isnot(None)) & (Task.ended_time.isnot(None)), func.extract('epoch', (Task.ended_time - Task.started_time)) ),
        else_=None
    )

    # 総作業時間（秒）を算出（started_time/ended_time が両方あるレコードのみ）
    total_duration_q = (
        db.session.query(func.sum(duration_expr).label('total_duration')).select_from(Task).filter(Task.started_time.isnot(None), Task.ended_time.isnot(None))
    )
    total_duration_q = _apply_year_month_filter(total_duration_q, date_column, year, month)
    total_duration_row = total_duration_q.first()
    total_seconds = total_duration_row.total_duration if total_duration_row and total_duration_row.total_duration is not None else None

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
        "total_hour": float(round(total_seconds / 3600, 1)) if total_seconds is not None else None,
        "total_day": int(total_day)
    })
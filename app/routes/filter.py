from babel.messages.extract import extract
from flask import Blueprint,request, redirect, url_for
from sqlalchemy import func
from app.models.task import Task
from app import db

filter_bp = Blueprint('filter', __name__)

@filter_bp.route("category", methods=['GET'])
def categories():
    category_all = db.session.query(Task.category_id).group_by(Task.category_id).all()
    return redirect("categories.html", category_all=category_all)

@filter_bp.route("category/<int:category_id>", methods=["GET"])
def category(category_id):
    todo_list = Task.query.filter_by(category_id=category_id).all()
    return redirect("category.html", todo_list=todo_list)

@filter_bp.route("/<int:year>/<int:month>", methods=["GET"])
def monthly(year, month):
    month_todo = db.session.query(
        extract('year', Task.started_date).label('year'),
        extract('month', Task.started_date).label('month'),
        func.sum(Task.duration_seconds).label('total_duration')
    ).filter(
        extract('year', Task.started_date) == year,
        extract('month', Task.started_date) == month,
    ).group_by(
        extract('year', Task.started_date),
        extract('month', Task.started_date)
    ).first
    # month_todo の中身（イメージ）
    # (2026, 2, 3600.0)

    return redirect("monthly.html", month_todo=month_todo)
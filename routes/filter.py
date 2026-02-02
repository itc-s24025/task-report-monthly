from babel.messages.extract import extract
from flask import Blueprint,request, redirect, url_for
from pygments.lexers import func

from modules.todo import db, Todo

filter_bp = Blueprint('filter', __name__)

@filter_bp.route("category", methods=['GET'])
def categories():
    category_all = db.session.query(Todo.category_id).group_by(Todo.category_id).all()
    return redirect("categories.html", category_all=category_all)

@filter_bp.route("category/<int:category_id>", methods=["GET"])
def category(category_id):
    todo_list = Todo.query.filter_by(category_id=category_id).all()
    return redirect("category.html", todo_list=todo_list)

@filter_bp.route("/<int:year>/<int:month>", methods=["GET"])
def monthly(year, month):
    month_todo = db.session.query(
        extract('year', Todo.started_by).label('year'),
        extract('month', Todo.started_by).label('month'),
        func.sum(Todo.duration).label('total_duration')
    ).filter(
        extract('year', Todo.started_by) == year,
        extract('month', Todo.started_by) == month,
    ).group_by(
        extract('year', Todo.started_by),
        extract('month', Todo.started_by)
    ).first
    # month_todo の中身（イメージ）
    # (2026, 2, 3600.0)

    return redirect("monthly.html", month_todo=month_todo)
from flask import Blueprint,request, redirect, url_for
from modules.todo import db, Todo

category_bp = Blueprint('filter', __name__)

@category_bp.route("category", methods=['GET'])
def categories():
    category_all = db.session.query(Todo.category_id).group_by(Todo.category_id).all()
    return redirect("categories.html", category_all=category_all)

@category_bp.route("category/<int:category_id>", methods=["GET"])
def category(category_id):
    todo_list = Todo.query.filter_by(category_id=category_id).all()
    return redirect("filter.html", todo_list=todo_list)
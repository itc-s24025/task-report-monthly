from flask import Blueprint, jsonify, session
from app import db
from app.models.category import Category

category_bp = Blueprint(
    "category",
    __name__,
    url_prefix="/api/categories"
)

@category_bp.route("", methods=["GET"])
def get_categories():
    """
    カテゴリ一覧取得（ログインユーザー用）
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    categories = db.session.execute(
        db.select(Category).where(Category.user_id == user_id)
    ).scalars().all()

    return jsonify([
        {
            "id": c.id,
            "category_name": c.category_name,
            "color": c.color
        }
        for c in categories
    ])

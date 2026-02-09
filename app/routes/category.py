from flask import Blueprint, jsonify, session, request
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


@category_bp.route("", methods=["POST"])
def create_category():
    """Create a new category for the logged-in user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}
    name = data.get("category_name")
    color = data.get("color") or "#888888"
    if not name:
        return jsonify({"error": "category_name required"}), 400

    cat = Category(
        user_id=user_id,
        category_name=name,
        color=color
    )
    db.session.add(cat)
    db.session.commit()

    return jsonify({"status": "created", "id": cat.id, "category_name": cat.category_name, "color": cat.color}), 201

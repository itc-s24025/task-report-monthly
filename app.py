from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import os

# =========================
# Flask アプリ初期化
# =========================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-me"
)

# =========================
# PostgreSQL 設定
# =========================
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://todo_user:"
    "todo_password@localhost/todo_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# Google OAuth 設定
# =========================
oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# =========================
# モデル定義
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="todos")


# =========================
# ログイン中ユーザー取得
# =========================
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


# =========================
# 画面ルーティング
# =========================
@app.route("/")
def home():
    """
    トップページ
    ログイン済み → カレンダー表示
    未ログイン → ログインボタン表示
    """
    user = get_current_user()
    return render_template("index.html", user=user)


# =========================
# Todo API（カレンダー用）
# =========================
@app.route("/api/todos", methods=["GET"])
def api_todos():
    """
    Todo 一覧取得（FullCalendar 用）
    """
    user = get_current_user()
    if not user:
        return jsonify([])

    todos = db.session.execute(
        db.select(Todo).where(Todo.user_id == user.id)
    ).scalars().all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "start": t.due_date.isoformat(),
            "color": "#999" if t.is_completed else "#3788d8"
        }
        for t in todos
    ])


# =========================
# Todo 新規追加（Create）
# =========================
@app.route("/add", methods=["POST"])
def add_todo():
    """
    日付クリックで Todo 追加
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    title = data.get("title")
    date_str = data.get("due_date")

    if not title or not date_str:
        return jsonify({"error": "invalid data"}), 400

    todo = Todo(
        title=title,
        due_date=datetime.strptime(date_str, "%Y-%m-%d").date(),
        user_id=user.id
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify({"status": "created"})


# =========================
# Todo 単件取得（Read）
# =========================
@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    todo = db.session.execute(
        db.select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user.id
        )
    ).scalar_one_or_none()

    if not todo:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "id": todo.id,
        "title": todo.title,
        "due_date": todo.due_date.isoformat(),
        "is_completed": todo.is_completed
    })


# =========================
# Todo 更新（Update）
# =========================
@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    todo = db.session.execute(
        db.select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user.id
        )
    ).scalar_one_or_none()

    if not todo:
        return jsonify({"error": "not found"}), 404

    data = request.get_json()

    if "title" in data:
        todo.title = data["title"]

    if "due_date" in data:
        todo.due_date = datetime.strptime(
            data["due_date"], "%Y-%m-%d"
        ).date()

    if "is_completed" in data:
        todo.is_completed = data["is_completed"]

    db.session.commit()
    return jsonify({"status": "updated"})


# =========================
# Todo 削除（Delete）
# =========================
@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    todo = db.session.execute(
        db.select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user.id
        )
    ).scalar_one_or_none()

    if not todo:
        return jsonify({"error": "not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"status": "deleted"})


# =========================
# Google ログイン処理
# =========================
@app.route("/login")
def login():
    return oauth.google.authorize_redirect(
        url_for("auth_callback", _external=True)
    )


@app.route("/auth/google/callback")
def auth_callback():
    oauth.google.authorize_access_token()
    userinfo = oauth.google.userinfo()

    google_id = userinfo["sub"]

    user = db.session.execute(
        db.select(User).where(User.google_id == google_id)
    ).scalar_one_or_none()

    if not user:
        user = User(
            google_id=google_id,
            name=userinfo.get("name"),
            email=userinfo.get("email"),
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# =========================
# アプリ起動
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

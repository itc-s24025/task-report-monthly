from flask import Blueprint, redirect, url_for, session, render_template
from app import db, oauth
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    user_id = session.get("user_id")
    user = db.session.get(User, user_id) if user_id else None
    return render_template(
        "index.html" if user else "login.html",
        user=user
    )


@auth_bp.route("/login")
def login():
    return oauth.google.authorize_redirect(
        url_for("auth.callback", _external=True)
    )


@auth_bp.route("/auth/google/callback")
def callback():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.userinfo()

    user = db.session.execute(
        db.select(User).where(User.google_id == userinfo["sub"])
    ).scalar_one_or_none()

    if not user:
        user = User(
            google_id=userinfo["sub"],
            name=userinfo.get("name"),
            email=userinfo.get("email"),
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    return redirect(url_for("auth.home"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))

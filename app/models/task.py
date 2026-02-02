from app import db
from datetime import datetime, date

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    task_name = db.Column(db.String(100), nullable=False)
    memo = db.Column(db.Text)

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    duration_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    created_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    category = db.relationship("Category")

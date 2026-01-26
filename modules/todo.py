# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .db_instance import db


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    title = db.Column(db.String(100), nullable=False)
    memo = db.Column(db.String(100))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    started_by = db.Column(db.DateTime)
    ended_by = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

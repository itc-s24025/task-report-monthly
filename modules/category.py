from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .db_instance import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), default="white")
    created_at = db.Column(db.DateTime, default=datetime.now())
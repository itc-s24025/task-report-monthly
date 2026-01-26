# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ここで db を作る（中身は空っぽ）

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

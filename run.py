from flask import render_template
from app import create_app, db

app = create_app()

@app.route("/report")
def report():
    return render_template("report.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

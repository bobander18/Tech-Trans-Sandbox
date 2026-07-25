from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    jsonify,
    g
)
import sqlite3
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)
from functools import wraps
from database import get_db, close_db
from auth import get_current_user, login_required
from blueprints.notes import notes_bp
import os

app = Flask(__name__)

app.teardown_appcontext(close_db)
app.register_blueprint(notes_bp)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "temporary-learning-key"
)

@app.route("/")
def home():
    user = get_current_user()
    if user is not None:
        return redirect(url_for("profile"))
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    if user is not None and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        return redirect(url_for("profile"))
    return render_template("index.html", error = "Incorrect Username or Password.")

@app.route("/profile")
def profile():
    user = get_current_user()
    if user is None:
        return render_template(
            "index.html",
            error="You must log in first."
        )
    return render_template("profile.html", username=user["username"])

@app.route("/api/profile")
@login_required
def api_profile():
    return jsonify({"username":g.user["username"]})

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

@app.route("/edit-profile", methods=["GET", "POST"])
def editprofile():
    if "user_id" not in session:
        return redirect(url_for("home"))
    user_id = session["user_id"]

    #POST
    if request.method == "POST":
        username = request.form["username"]
        db = get_db()
        db.execute("""
            UPDATE users
            SET username = ?
            WHERE id = ?
            """,
            (username, user_id)
            )
        db.commit()
        return redirect(url_for("profile"))

    #GET
    user = get_current_user()
    return render_template("editprofile.html", username=user["username"])

@app.route("/delete-account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        user_id = session["user_id"]
        db = get_db()
        db.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
            )
        db.commit()
        session.pop("user_id", None)
        return redirect(url_for("home"))
    return render_template("deleteaccount.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    #POST
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            return render_template(
                "register.html",
                error="Username and password are required."
            )
        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters."
            )
        password_hash = generate_password_hash(password)
        db = get_db()
        existing_user = db.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if existing_user:
            return render_template(
                "register.html",
                error="That username is already taken."
            )
        try:
            db.execute("""
                INSERT INTO users
                (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash)
            )
            db.commit()
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="That username is already taken."
            )
        flash("Account created successfully!")
        return redirect(url_for("home"))

    #GET
    return render_template("register.html")

@app.route("/notes")
def notes():
    if "user_id" not in session:
        return redirect(url_for("home"))
    return render_template("notes.html")

if __name__ == "__main__":
    app.run(debug=True)
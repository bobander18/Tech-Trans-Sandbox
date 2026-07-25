from database import get_db, close_db
from flask import session, g, jsonify
from functools import wraps

def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    db = get_db()
    user = db.execute("""
        SELECT id, username
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()
    return user

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Not logged in"}), 401
        g.user = user
        return func(*args, **kwargs)
    return wrapper
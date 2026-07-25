from flask import Blueprint
from auth import login_required
from database import get_db
from flask import (
    jsonify,
    g,
    request,
    session,
    url_for,
    render_template,
    redirect)
import math

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

@notes_bp.route("/", methods=["GET", "POST"])
@login_required
def api_notes():
    db = get_db()
    #GET
    search = request.args.get("search","")
    page = request.args.get("page",1,type=int)
    limit = 5
    offset = (page - 1)*limit
    searchLike = "%"+search+"%"
    print(search)
    if request.method == "GET":
        noteCount = db.execute("""
            SELECT COUNT(id) AS total
            FROM notes
            WHERE user_id = ?
            AND (
                title LIKE ?
                OR content LIKE ?
            )
            """,
            (g.user["id"], searchLike, searchLike)
        ).fetchone()
        totalNotes = noteCount["total"]
        totalPages = max(1, math.ceil(totalNotes/limit))
        notes = db.execute("""
            SELECT id, title, content
            FROM notes
            WHERE user_id = ?
            AND (
                title LIKE ?
                OR content LIKE ?
            )
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (g.user["id"], searchLike, searchLike, limit, offset)
        ).fetchall()
        notes_list = []
        for note in notes:
            notes_list.append({
                "id": note["id"],
                "title": note["title"],
                "content": note["content"]
            })
        return jsonify({
            "notes":notes_list,
            "totalPages":totalPages})
    
    #POST
    data = request.get_json()
    title = data["title"].strip()
    content = data["content"].strip()
    if not title and not content:
        return jsonify({"error": "Note cannot be blank"}), 400
    cursor = db.execute("""
        INSERT INTO notes
        (title, content, user_id)
        VALUES (?, ?, ?)
        """,
        (title, content, g.user["id"])
    )
    note_id = cursor.lastrowid
    db.commit()
    return jsonify({
        "success":True,
        "note_id":note_id
    }), 201

@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    db = get_db()
    db.execute("""
        DELETE FROM notes
        WHERE id = ? AND user_id = ?
        """, (note_id, g.user["id"])
    )
    db.commit()
    return jsonify({"success":True})

@notes_bp.route("/<int:note_id>", methods=["PUT"])
@login_required
def update_note(note_id):
    db = get_db()
    data = request.get_json()
    title = data["title"]
    content = data["content"]
    db.execute("""
    UPDATE notes
    SET title = ?, content = ?
    WHERE id = ? AND user_id = ?
    """, (title, content, note_id, g.user["id"])
    )
    db.commit()
    return jsonify({"success": True})
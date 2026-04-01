import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "todo.db"

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                priority TEXT NOT NULL DEFAULT 'medium'
            )
        """)
        # Migrate existing DB: add priority column if it doesn't exist
        cols = [row[1] for row in conn.execute("PRAGMA table_info(todos)").fetchall()]
        if "priority" not in cols:
            conn.execute("ALTER TABLE todos ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")


@app.route("/")
def index():
    sort = request.args.get("sort", "id")
    with get_db() as conn:
        if sort == "priority":
            todos = conn.execute(
                "SELECT * FROM todos ORDER BY CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, id DESC"
            ).fetchall()
        else:
            todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return render_template("index.html", todos=todos, sort=sort)


@app.route("/create", methods=["POST"])
def create():
    title = request.form["title"].strip()
    priority = request.form.get("priority", "medium")
    if priority not in PRIORITY_ORDER:
        priority = "medium"
    if title:
        with get_db() as conn:
            conn.execute("INSERT INTO todos (title, priority) VALUES (?, ?)", (title, priority))
    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if priority not in PRIORITY_ORDER:
        priority = "medium"
    if title:
        with get_db() as conn:
            conn.execute("UPDATE todos SET title = ?, priority = ? WHERE id = ?", (title, priority, todo_id))
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    with get_db() as conn:
        todo = conn.execute("SELECT done FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if todo:
            conn.execute("UPDATE todos SET done = ? WHERE id = ?", (1 - todo["done"], todo_id))
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
